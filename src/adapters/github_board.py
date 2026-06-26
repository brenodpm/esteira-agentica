"""GitHub Board Adapter - implementa BoardPort para GitHub Projects V2."""

import json
import subprocess
import time
import re
from datetime import datetime, timedelta

from src.core.board import BoardPort, Issue, PenaltyException
from src.core.log import log


class GitHubBoardAdapter(BoardPort):
    """Adapter para GitHub Projects V2."""

    # Penalty
    _in_penalty: bool = False
    _penalty_ttl: datetime = None
    _penalty_value: int = 1
    _penalty_cooldown: datetime = None

    # Throttle
    _throttle_value: int = 16
    _throttle_cooldown: datetime = None

    # Offline (sem conexão) - backoff de reconexão
    _offline_value: int = 1
    _offline_max: int = 300

    # Config
    _repo: str = None

    # Cache de metadados por board_id (preenchido em sync_boards):
    # {board_id: {project_id, status_field_id, options: {col: option_id}}}
    _projects: dict = None

    def _board_meta(self, board_id: str) -> dict:
        """Retorna metadados cacheados do board ou levanta erro se ausente."""
        meta = (self._projects or {}).get(board_id)
        if not meta:
            raise Exception(
                f"Board '{board_id}' não resolvido - execute sync_boards antes"
            )
        return meta

    def _penalty_check(self):
        if self._in_penalty:
            if self._penalty_ttl and self._penalty_ttl > datetime.now():
                remaining = max(1, int((self._penalty_ttl - datetime.now()).total_seconds()))
                raise PenaltyException(remaining)
            else:
                self._in_penalty = False
                log.info("GitHub", "Penalty desativado")
                self._penalty_cooldown = datetime.now() + timedelta(hours=1)

        if self._penalty_cooldown is None:
            self._penalty_cooldown = datetime.now() + timedelta(hours=1)

        if self._penalty_cooldown < datetime.now():
            if self._penalty_value > 1:
                self._penalty_value //= 2
            self._penalty_cooldown = datetime.now() + timedelta(hours=1)

    def _penalty_hit(self) -> PenaltyException:
        self._penalty_ttl = datetime.now() + timedelta(hours=self._penalty_value)
        self._penalty_value *= 2
        self._in_penalty = True
        log.warning("GitHub", f"Penalty ativado por {self._penalty_value // 2}h")
        remaining = int((self._penalty_ttl - datetime.now()).total_seconds())
        return PenaltyException(remaining)

    def _throttle(self):
        if self._throttle_cooldown is None:
            self._throttle_cooldown = datetime.now() + timedelta(hours=1)

        if self._throttle_cooldown < datetime.now():
            if self._throttle_value > 1:
                self._throttle_value //= 2
            self._throttle_cooldown = datetime.now() + timedelta(hours=1)

        time.sleep(self._throttle_value)

    def _throttle_hit(self):
        if self._throttle_value >= 64:
            raise self._penalty_hit()

        self._throttle_value = min(self._throttle_value * 2, 64)
        self._throttle_cooldown = datetime.now() + timedelta(hours=1)
        log.info("GitHub", f"Throttle aumentado para {self._throttle_value}s")

    def _extract_retry_after(self, text: str) -> int | None:
        """Extrai retry-after de headers ou mensagem de erro."""
        m = re.search(r'retry.?after[:\s]+(\d+)', text, re.IGNORECASE)
        if m:
            return int(m.group(1))
        return None

    def _get_rate_limit_reset(self) -> int | None:
        """Consulta tempo até reset do primary rate limit."""
        try:
            result = subprocess.run(
                ["gh", "api", "rate_limit"],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                return None
            data = json.loads(result.stdout)
            resources = data.get("resources", {})
            for key in ("graphql", "core"):
                r = resources.get(key, {})
                if r.get("remaining", 1) == 0:
                    return r.get("reset", 0) - int(time.time()) + 5
            return None
        except Exception:
            return None

    def _handle_rate_limit(self, output: str, error: str) -> bool:
        """Detecta e trata rate limit a partir da saída do gh.

        Retorna True se era rate limit (já aguardou; caller deve repetir a chamada),
        False caso contrário.
        """
        combined = f"{output} {error}".lower()
        if "rate limit" not in combined and "secondary rate limit" not in combined:
            return False

        # Secondary rate limit (tem retry-after)
        if self._extract_retry_after(f"{output} {error}"):
            wait = self._throttle_value * 8
            back_at = (datetime.now() + timedelta(seconds=wait)).strftime("%H:%M:%S")
            log.warning("GitHub", f"[{self._throttle_value}s] Secondary rate limit - retorna às {back_at}",
                        wait_seconds=wait, error=error[:200])
            self._throttle_hit()
            time.sleep(wait)
            return True

        # Primary rate limit - buscar tempo de reset
        reset_time = self._get_rate_limit_reset()
        if reset_time and reset_time > 0:
            back_at = (datetime.now() + timedelta(seconds=reset_time)).strftime("%H:%M:%S")
            log.warning("GitHub", f"[{self._throttle_value}s] Primary rate limit - retorna às {back_at}",
                        wait_seconds=reset_time, error=error[:200])
            time.sleep(reset_time)
            return True

        # Fallback
        back_at = (datetime.now() + timedelta(seconds=60)).strftime("%H:%M:%S")
        log.warning("GitHub", f"[{self._throttle_value}s] Rate limit sem tempo definido - retorna às {back_at}",
                    wait_seconds=60, error=error[:200])
        time.sleep(60)
        return True

    def _handle_offline(self, output: str, error: str) -> bool:
        """Detecta falta de conexão a partir da saída do gh.

        Erro transitório: aguarda um backoff crescente (até _offline_max) e
        sinaliza retry. Não derruba a esteira. Retorna True se era offline.
        """
        combined = f"{output} {error}".lower()
        offline_signs = (
            "error connecting to",
            "could not resolve host",
            "no such host",
            "network is unreachable",
            "connection refused",
            "connection reset",
            "timeout",
            "timed out",
            "temporary failure in name resolution",
            "dial tcp",
        )
        if not any(sign in combined for sign in offline_signs):
            return False

        wait = self._offline_value
        back_at = (datetime.now() + timedelta(seconds=wait)).strftime("%H:%M:%S")
        log.warning("GitHub", f"Sem conexão - nova tentativa às {back_at}",
                    wait_seconds=wait, attempt=self._offline_value, error=error[:200])
        time.sleep(wait)
        self._offline_value = min(self._offline_value * 2, self._offline_max)
        return True

    def _gh(self, *args) -> str:
        """Executa comando gh com tratamento de rate limit e falta de conexão."""
        attempt = 0
        while True:
            attempt += 1
            if attempt > 1:
                log.info("GitHub", f"[{self._throttle_value}s] Tentando novamente (tentativa {attempt})",
                         attempt=attempt, command=args[0] if args else "")
            self._throttle()
            result = subprocess.run(["gh", *args], capture_output=True, text=True)
            output = result.stdout.strip()
            error = result.stderr.strip()

            if self._handle_rate_limit(output, error):
                continue

            if result.returncode != 0 and self._handle_offline(output, error):
                continue

            if result.returncode != 0:
                raise Exception(error or output or f"gh retornou código {result.returncode}")

            self._offline_value = 1
            return output

    def _gql(self, query: str, **variables) -> dict:
        """Executa query GraphQL com tratamento de rate limit e falta de conexão."""
        attempt = 0
        while True:
            attempt += 1
            if attempt > 1:
                log.info("GitHub", f"[{self._throttle_value}s] Tentando novamente (tentativa {attempt})",
                         attempt=attempt, query=query[:80])
            self._throttle()
            args = ["gh", "api", "graphql", "-f", f"query={query}"]
            for k, v in variables.items():
                flag = "-F" if isinstance(v, (int, float, bool)) else "-f"
                args += [flag, f"{k}={v}"]

            result = subprocess.run(args, capture_output=True, text=True)
            output = result.stdout.strip()
            error = result.stderr.strip()

            if self._handle_rate_limit(output, error):
                continue

            if result.returncode != 0 and self._handle_offline(output, error):
                continue

            if not output:
                raise Exception(error or "Resposta vazia do GraphQL")

            data = json.loads(output)
            if "errors" in data and "data" not in data:
                raise Exception(str(data["errors"]))

            self._offline_value = 1
            return data.get("data", {})

    def _resolve_owner(self, owner: str) -> tuple[str, str]:
        log.info("GitHub", f"[{self._throttle_value}s] {owner} - Resolvendo owner",
                 operation="resolve_owner", owner=owner)
        data = self._gql(
            "query($login:String!){organization(login:$login){id} user(login:$login){id}}",
            login=owner,
        )
        if data.get("organization") and data["organization"].get("id"):
            return data["organization"]["id"], "organization"
        return data["user"]["id"], "user"

    def _list_projects(self, owner: str, owner_type: str) -> list[dict]:
        log.info("GitHub", f"[{self._throttle_value}s] {owner} - Listando projects",
                 operation="list_projects", owner=owner, owner_type=owner_type)
        entity = "organization" if owner_type == "organization" else "user"
        query = f"query($login:String!){{{entity}(login:$login){{projectsV2(first:50){{nodes{{id number title}}}}}}}}"
        data = self._gql(query, login=owner)
        return data[entity]["projectsV2"]["nodes"]

    def _create_project(self, owner_id: str, title: str) -> dict:
        log.info("GitHub", f"[{self._throttle_value}s] {title} - Criando project",
                 operation="create_project", owner_id=owner_id, title=title)
        data = self._gql(
            "mutation($ownerId:ID!,$title:String!){createProjectV2(input:{ownerId:$ownerId,title:$title}){projectV2{id number title}}}",
            ownerId=owner_id,
            title=title,
        )
        return data["createProjectV2"]["projectV2"]

    def _get_status_field(self, project_id: str) -> dict | None:
        log.info("GitHub", f"[{self._throttle_value}s] {project_id[:8]}... - Buscando campo Status",
                 operation="get_status_field", project_id=project_id)
        data = self._gql(
            "query($id:ID!){node(id:$id){...on ProjectV2{fields(first:20){nodes{...on ProjectV2SingleSelectField{id name options{id name}}}}}}}",
            id=project_id,
        )
        for field in data["node"]["fields"]["nodes"]:
            if field.get("name") == "Status":
                return field
        return None

    def _create_status_field(self, project_id: str, columns: list[str]) -> None:
        log.info("GitHub", f"[{self._throttle_value}s] {project_id[:8]}... - Criando campo Status",
                 operation="create_status_field", project_id=project_id, columns=columns)
        opts = "[" + ",".join(f'{{name:"{col}",color:GRAY,description:""}}' for col in columns) + "]"
        self._gql(
            f'mutation($pid:ID!){{createProjectV2Field(input:{{projectId:$pid,dataType:SINGLE_SELECT,name:"Status",singleSelectOptions:{opts}}}){{projectV2Field{{...on ProjectV2SingleSelectField{{id}}}}}}}}',
            pid=project_id,
        )

    def _update_status_options(self, field_id: str, columns: list[str], existing: dict[str, str]) -> None:
        log.info("GitHub", f"[{self._throttle_value}s] {field_id[:8]}... - Atualizando opções do Status",
                 operation="update_status_options", field_id=field_id, columns=columns)
        parts = []
        for col in columns:
            if col in existing:
                parts.append(f'{{id:"{existing[col]}",name:"{col}",color:GRAY,description:""}}')
            else:
                parts.append(f'{{name:"{col}",color:GRAY,description:""}}')
        opts = "[" + ",".join(parts) + "]"
        self._gql(
            f'mutation($fid:ID!){{updateProjectV2Field(input:{{fieldId:$fid,singleSelectOptions:{opts}}}){{projectV2Field{{...on ProjectV2SingleSelectField{{id}}}}}}}}',
            fid=field_id,
        )

    def connect(self, config: dict) -> None:
        repos = config.get("git", {}).get("repo", {})
        self._repo = list(repos.values())[0] if repos else None
        if self._repo and self._repo.startswith("git@github.com:"):
            self._repo = self._repo.replace("git@github.com:", "").replace(".git", "")
        log.info("GitHub", f"Repositório: {self._repo}")

    def sync_boards(self, boards: list[dict]) -> None:
        self._penalty_check()

        if not self._repo:
            log.warning("GitHub", "Repositório não configurado")
            return

        if self._projects is None:
            self._projects = {}

        owner = self._repo.split("/")[0]
        owner_id, owner_type = self._resolve_owner(owner)
        projects = self._list_projects(owner, owner_type)
        projects_by_title = {p["title"]: p for p in projects}

        for board in boards:
            board_id = board["id"]
            board_name = board["name"]
            columns = board["columns"]

            project = projects_by_title.get(board_name)
            if not project:
                log.info("GitHub", f"Criando board '{board_name}'")
                project = self._create_project(owner_id, board_name)
                projects_by_title[board_name] = project

            status_field = self._get_status_field(project["id"])
            if not status_field:
                log.info("GitHub", f"Criando campo Status para '{board_name}'")
                self._create_status_field(project["id"], columns)
                status_field = self._get_status_field(project["id"])
            else:
                existing = {o["name"]: o["id"] for o in status_field.get("options", [])}
                current_order = [o["name"] for o in status_field.get("options", [])]
                if current_order != columns:
                    log.info("GitHub", f"Atualizando colunas de '{board_name}'")
                    self._update_status_options(status_field["id"], columns, existing)
                    status_field = self._get_status_field(project["id"])

            # Cacheia metadados para list_issues/move_issue
            self._projects[board_id] = {
                "project_id": project["id"],
                "status_field_id": status_field["id"] if status_field else None,
                "options": {
                    o["name"]: o["id"]
                    for o in (status_field.get("options", []) if status_field else [])
                },
            }

        log.info("GitHub", "Boards sincronizados")

    def list_issues(self, board_id: str) -> list[Issue]:
        self._penalty_check()
        meta = self._board_meta(board_id)
        project_id = meta["project_id"]

        log.info("GitHub", f"[{self._throttle_value}s] {board_id} - Listando issues",
                 operation="list_issues", board_id=board_id, project_id=project_id)

        query = """query($pid:ID!,$cursor:String){
          node(id:$pid){...on ProjectV2{
            items(first:5,after:$cursor){
              pageInfo{hasNextPage endCursor}
              nodes{
                id
                isArchived
                fieldValues(first:10){nodes{...on ProjectV2ItemFieldSingleSelectValue{field{...on ProjectV2SingleSelectField{name}} name}}}
                content{...on Issue{number title body updatedAt labels(first:20){nodes{name}}}}
              }
            }
          }}
        }"""

        issues: list[Issue] = []
        cursor = ""
        page_num = 0
        while True:
            page_num += 1
            if page_num > 1:
                log.info("GitHub", f"[{self._throttle_value}s] {board_id} - Página {page_num}",
                         operation="list_issues_page", board_id=board_id, page=page_num)
            data = self._gql(query, pid=project_id, cursor=cursor) if cursor \
                else self._gql(query, pid=project_id)

            node = data.get("node") or {}
            page = node.get("items", {})
            for item in page.get("nodes", []):
                if item.get("isArchived"):
                    continue
                content = item.get("content")
                if not content or not content.get("number"):
                    continue

                column = ""
                for fv in item.get("fieldValues", {}).get("nodes", []):
                    if (fv.get("field") or {}).get("name") == "Status":
                        column = fv.get("name", "")
                        break

                labels = [
                    l["name"]
                    for l in (content.get("labels", {}) or {}).get("nodes", [])
                ]

                issues.append(Issue(
                    id=str(content["number"]),
                    title=content.get("title", ""),
                    body=content.get("body", ""),
                    column=column,
                    labels=labels,
                    updated_at=content.get("updatedAt", ""),
                ))

            page_info = page.get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break
            cursor = page_info["endCursor"]

        return issues

    def get_issue(self, board_id: str, issue_id: str) -> Issue:
        pass

    def move_issue(self, board_id: str, issue_id: str, column: str) -> None:
        pass

    def update_issue(self, board_id: str, issue_id: str, title: str = None, body: str = None) -> None:
        pass

    def add_comment(self, board_id: str, issue_id: str, comment: str) -> None:
        pass
