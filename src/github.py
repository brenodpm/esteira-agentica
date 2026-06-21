"""Integração com GitHub Projects V2 via gh CLI (GraphQL)."""

import json
import subprocess
import time
from pathlib import Path

from src.log import log

_SNAPSHOT_FILE = Path(".pipe/snapshot.json")

_last_mutation_time = 0.0
_last_api_time = 0.0
_base_interval = 2.0
_api_interval = 2.0  # intervalo entre chamadas (segundos) — adaptativo
_max_throttle = 30.0
_default_retry_after = 60
_cooldown = 600  # segundos sem throttle antes de regredir (10 min)
_last_throttle_time = 0.0  # timestamp da última progressão

# Penalty box
_penalty_base = 3600
_penalty_max = 86400
_penalty_cooldown = 3600
_penalty_duration = 0  # duração atual (0 = inativo)
_penalty_until = 0.0  # timestamp até quando está em penalty
_penalty_last_hit = 0.0  # timestamp da última ativação


def configure(config: dict) -> None:
    """Inicializa parâmetros de throttle e penalty a partir de pipe.github."""
    global _base_interval, _api_interval, _max_throttle, _default_retry_after, _cooldown
    global _penalty_base, _penalty_max, _penalty_cooldown
    gh_cfg = config.get("pipe", {}).get("github", {})
    _base_interval = float(gh_cfg.get("throttle", 2))
    _api_interval = _base_interval
    _max_throttle = float(gh_cfg.get("max-throttle", 30))
    _default_retry_after = int(gh_cfg.get("retry-after", 60))
    _cooldown = int(gh_cfg.get("cooldown", 600))
    pen = gh_cfg.get("penalty", {})
    _penalty_base = int(pen.get("base", 3600))
    _penalty_max = int(pen.get("max", 86400))
    _penalty_cooldown = int(pen.get("cooldown", 3600))
    _load_state()


def _save_state():
    """Persiste estado de throttle e penalty no snapshot."""
    if not _SNAPSHOT_FILE.exists():
        return
    snapshot = json.loads(_SNAPSHOT_FILE.read_text())
    snapshot["throttle"] = {
        "interval": _api_interval,
        "last_hit": _last_throttle_time,
        "penalty_duration": _penalty_duration,
        "penalty_until": _penalty_until,
        "penalty_last_hit": _penalty_last_hit,
    }
    _SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))


def _load_state():
    """Restaura estado de throttle e penalty do snapshot."""
    global _api_interval, _last_throttle_time
    global _penalty_duration, _penalty_until, _penalty_last_hit
    if not _SNAPSHOT_FILE.exists():
        return
    snapshot = json.loads(_SNAPSHOT_FILE.read_text())
    state = snapshot.get("throttle")
    if not state:
        return
    _api_interval = max(float(state.get("interval", _base_interval)), _base_interval)
    _last_throttle_time = float(state.get("last_hit", 0))
    _penalty_duration = int(state.get("penalty_duration", 0))
    _penalty_until = float(state.get("penalty_until", 0))
    _penalty_last_hit = float(state.get("penalty_last_hit", 0))
    if _penalty_until > time.time():
        from datetime import datetime, timezone, timedelta
        _tz = timezone(timedelta(hours=-3))
        wake = datetime.fromtimestamp(_penalty_until, _tz)
        log.info("[Penalty] Restaurado — retorno às %s", wake.strftime("%H:%M:%S"))
    elif _api_interval > _base_interval:
        log.info("[Throttle] Restaurado — intervalo %.1fs", _api_interval)


def is_in_penalty() -> bool:
    """Retorna True se estamos em penalty box (API bloqueada)."""
    global _penalty_duration, _penalty_until
    if _penalty_until <= 0:
        return False
    if time.time() >= _penalty_until:
        # Penalty expirou — tentar regredir
        _penalty_regress()
        return False
    return True


def penalty_remaining() -> int:
    """Retorna segundos restantes de penalty, ou 0 se inativo."""
    if _penalty_until <= 0:
        return 0
    remaining = _penalty_until - time.time()
    return max(0, int(remaining))


def _penalty_activate():
    """Ativa ou progride o penalty box."""
    global _penalty_duration, _penalty_until, _penalty_last_hit, _api_interval
    _penalty_last_hit = time.time()
    if _penalty_duration == 0:
        _penalty_duration = _penalty_base
    else:
        _penalty_duration = min(_penalty_duration * 2, _penalty_max)
    _penalty_until = time.time() + _penalty_duration
    from datetime import datetime, timezone, timedelta
    _tz = timezone(timedelta(hours=-3))
    wake = datetime.now(_tz) + timedelta(seconds=_penalty_duration)
    log.warning("[Penalty] Ativado — duração %ds — retorno às %s", _penalty_duration, wake.strftime("%H:%M:%S"))


def _penalty_regress():
    """Regride ou desativa o penalty box."""
    global _penalty_duration, _penalty_until, _api_interval, _last_throttle_time
    elapsed = time.time() - _penalty_last_hit
    if elapsed >= _penalty_cooldown and _penalty_duration > 0:
        _penalty_duration = _penalty_duration // 2
        if _penalty_duration < _penalty_base:
            _penalty_duration = 0
        log.info("[Penalty] Regredido — nível %ds", _penalty_duration)
    _penalty_until = 0
    # Reset throttle ao sair do penalty
    _api_interval = _base_interval
    _last_throttle_time = 0.0
    log.info("[Penalty] Desativado — throttle reset para %.1fs", _api_interval)
    _save_state()


def _api_throttle():
    """Garante intervalo mínimo entre chamadas API consecutivas."""
    global _last_api_time
    elapsed = time.time() - _last_api_time
    if elapsed < _api_interval:
        time.sleep(_api_interval - elapsed)
    _last_api_time = time.time()


def _on_rate_limit_hit():
    """Chamado quando secondary rate limit é atingido. Dobra o intervalo ou ativa penalty."""
    global _api_interval, _last_throttle_time
    _last_throttle_time = time.time()
    if _api_interval >= _max_throttle:
        # Throttle no máximo e ainda falha → ativar penalty box
        _penalty_activate()
    else:
        _api_interval = min(_api_interval * 2, _max_throttle)
        log.info("[Throttle] Intervalo → %.1fs", _api_interval)
    _save_state()


def _on_api_success():
    """Chamado após chamada bem-sucedida. Regride intervalo se cooldown expirou."""
    global _api_interval, _last_throttle_time
    if _api_interval <= _base_interval:
        return
    elapsed = time.time() - _last_throttle_time
    if elapsed >= _cooldown:
        _api_interval = max(_api_interval / 2, _base_interval)
        _last_throttle_time = time.time()
        log.info("[Throttle] Intervalo ← %.1fs (cooldown %ds ok)", _api_interval, _cooldown)
        _save_state()


def _mutation_throttle():
    """Garante 1s de intervalo entre mutations consecutivas."""
    global _last_mutation_time
    elapsed = time.time() - _last_mutation_time
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)
    _last_mutation_time = time.time()


class GitHubError(Exception):
    """Erro genérico de comunicação com GitHub."""


class RateLimitError(GitHubError):
    """Rate limit atingido."""

    def __init__(self, msg="GitHub API rate limit excedido", reset_at: float = 0, retry_after: int = 0):
        super().__init__(msg)
        self.reset_at = reset_at
        self.retry_after = retry_after


def get_rate_limit_reset() -> float:
    """Consulta GitHub API para obter timestamp Unix de quando o rate limit reseta.

    Retorna o timestamp do reset se remaining==0 (primary rate limit).
    Retorna 0 se é secondary rate limit (remaining > 0 mas API retornou 403).
    """
    try:
        result = subprocess.run(
            ["gh", "api", "rate_limit"], capture_output=True, text=True
        )
        if result.returncode != 0:
            return 0
        data = json.loads(result.stdout)
        resources = data.get("resources", {})
        resets = []
        for key in ("graphql", "core"):
            r = resources.get(key, {})
            if r.get("remaining", 1) == 0:
                resets.append(r.get("reset", 0))
        return min(resets) if resets else 0
    except Exception:
        return 0


def get_graphql_rate_info() -> dict:
    """Consulta rateLimit via GraphQL. Retorna {cost, remaining, resetAt} ou {}."""
    try:
        result = subprocess.run(
            ["gh", "api", "graphql", "-f", "query=query{rateLimit{cost remaining resetAt}}"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return {}
        data = json.loads(result.stdout)
        return data.get("data", {}).get("rateLimit", {})
    except Exception:
        return {}


def sleep_until_rate_limit_reset(fallback: int = 60, retry_after: int = 0) -> None:
    """Dorme até o rate limit resetar.

    Prioridade: retry_after > primary reset time > fallback.
    """
    from datetime import datetime, timezone, timedelta
    _tz = timezone(timedelta(hours=-3))

    # 1. Se temos retry_after explícito (secondary rate limit)
    if retry_after > 0:
        wake = datetime.now(_tz) + timedelta(seconds=retry_after)
        log.info("[Throttle] Aguardando %ds — retorno às %s", retry_after, wake.strftime("%H:%M:%S"))
        time.sleep(retry_after)
        return

    # 2. Tentar obter primary reset time
    reset_ts = get_rate_limit_reset()
    if reset_ts:
        wait = reset_ts - time.time() + 5
        if wait > 0:
            wake = datetime.now(_tz) + timedelta(seconds=wait)
            log.warning("[GitHub] Rate limit reset em %ds — retorno às %s", int(wait), wake.strftime("%H:%M:%S"))
            time.sleep(wait)
            return

    # 3. Fallback
    wake = datetime.now(_tz) + timedelta(seconds=fallback)
    log.warning("[GitHub] Não foi possível obter reset time — retorno às %s (%ds)", wake.strftime("%H:%M:%S"), fallback)
    time.sleep(fallback)


def _extract_retry_after(text: str) -> int:
    """Extrai retry-after (em segundos) de mensagens de erro do gh CLI.

    Se não há header explícito, escala com o nível de throttle atual
    (exponential backoff conforme recomendação do GitHub).
    """
    import re
    # Header Retry-After no stderr do gh
    m = re.search(r'retry.?after[:\s]+(\d+)', text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    # Escalar: base retry * (intervalo_atual / intervalo_base)
    # Ex: 60s base, intervalo 4x → 120s; intervalo 8x → 240s
    scale = max(1, int(_api_interval / _base_interval))
    return _default_retry_after * scale


def _gh(*args) -> str:
    _api_throttle()
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    output = result.stdout.strip()
    error = result.stderr.strip()

    if "rate limit" in output.lower() or "rate limit" in error.lower():
        retry = _extract_retry_after(error + " " + output)
        _on_rate_limit_hit()
        log.debug("[GitHub] Rate limit na chamada: gh %s", " ".join(args[:3]))
        raise RateLimitError("GitHub API rate limit excedido", retry_after=retry)

    if result.returncode != 0:
        log.debug("[GitHub] gh %s → erro: %s", " ".join(args[:3]), error or output)
        raise GitHubError(error or output or f"gh retornou código {result.returncode}")

    _on_api_success()
    return result.stdout


def _gql(query: str, **variables) -> dict:
    _api_throttle()
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        flag = "-F" if isinstance(v, (int, float, bool)) else "-f"
        args += [flag, f"{k}={v}"]
    result = subprocess.run(args, capture_output=True, text=True)
    output = result.stdout.strip()
    error = result.stderr.strip()

    if "rate limit" in output.lower() or "rate limit" in error.lower():
        retry = _extract_retry_after(error + " " + output)
        _on_rate_limit_hit()
        log.debug("[GitHub] Rate limit na chamada GraphQL")
        raise RateLimitError("GitHub API rate limit excedido", retry_after=retry)

    if not output:
        raise GitHubError(error or "Resposta vazia do GraphQL")

    data = json.loads(output)
    if "errors" in data and "data" not in data:
        raise GitHubError(str(data["errors"]))
    _on_api_success()
    return data.get("data", {})


def _resolve_owner(owner: str) -> tuple[str, str]:
    data = _gql(
        "query($login:String!){organization(login:$login){id} user(login:$login){id}}",
        login=owner,
    )
    if data.get("organization") and data["organization"].get("id"):
        return data["organization"]["id"], "organization"
    return data["user"]["id"], "user"


def _list_projects(owner: str, owner_type: str) -> list[dict]:
    entity = "organization" if owner_type == "organization" else "user"
    query = f"query($login:String!){{{entity}(login:$login){{projectsV2(first:50){{nodes{{id number title}}}}}}}}"
    data = _gql(query, login=owner)
    return data[entity]["projectsV2"]["nodes"]


def _get_status_field(project_id: str) -> dict | None:
    data = _gql(
        "query($id:ID!){node(id:$id){...on ProjectV2{fields(first:20){nodes{...on ProjectV2SingleSelectField{id name options{id name}}}}}}}",
        id=project_id,
    )
    for field in data["node"]["fields"]["nodes"]:
        if field.get("name") == "Status":
            return field
    return None


def _get_all_status_fields(project_ids: list[str]) -> dict[str, dict | None]:
    """Busca campo Status de múltiplos projects em 1 query GraphQL (aliases).

    Retorna {project_id: {id, name, options} | None}.
    """
    if not project_ids:
        return {}
    # Montar query com aliases: p0, p1, p2...
    fragments = []
    for i, pid in enumerate(project_ids):
        fragments.append(
            f'p{i}:node(id:"{pid}"){{...on ProjectV2{{fields(first:20){{nodes{{...on ProjectV2SingleSelectField{{id name options{{id name}}}}}}}}}}}}'
        )
    query = "query{" + " ".join(fragments) + "}"
    data = _gql(query)

    result = {}
    for i, pid in enumerate(project_ids):
        node = data.get(f"p{i}", {})
        status = None
        for field in node.get("fields", {}).get("nodes", []):
            if field.get("name") == "Status":
                status = field
                break
        result[pid] = status
    return result


def _create_project(owner_id: str, title: str) -> dict:
    _mutation_throttle()
    data = _gql(
        "mutation($ownerId:ID!,$title:String!){createProjectV2(input:{ownerId:$ownerId,title:$title}){projectV2{id number title}}}",
        ownerId=owner_id,
        title=title,
    )
    return data["createProjectV2"]["projectV2"]


def _add_status_options(field_id: str, options: list[dict]) -> None:
    """Atualiza opções do campo Status. options: [{name, id?}, ...] na ordem desejada."""
    log.info("[GitHub] Atualizando opções do field %s com: %s", field_id, [o["name"] for o in options])
    _mutation_throttle()
    parts = []
    for o in options:
        if o.get("id"):
            parts.append(f'{{id:"{o["id"]}",name:"{o["name"]}",color:GRAY,description:""}}')
        else:
            parts.append(f'{{name:"{o["name"]}",color:GRAY,description:""}}')
    opts = "[" + ",".join(parts) + "]"
    log.debug("[GitHub] Mutation payload: %s", opts)
    _gql(
        f'mutation($fid:ID!){{updateProjectV2Field(input:{{fieldId:$fid,singleSelectOptions:{opts}}}){{projectV2Field{{...on ProjectV2SingleSelectField{{id}}}}}}}}',
        fid=field_id,
    )
    log.info("[GitHub] Mutation executada com sucesso")


def resolve_project_metadata(config: dict, board_id: str, cache: dict) -> dict:
    """Resolve project_id, status_field_id e options usando cache.

    Retorna dict com: project_id, project_number, status_field_id, options.
    Se cache válido: 0 chamadas. Se não: 2 chamadas (list_projects + get_status_field).
    Atualiza o cache in-place.
    """
    board_cache = cache.get(board_id)
    if board_cache and board_cache.get("project_id") and board_cache.get("status_field_id"):
        return board_cache

    owner = config["repo"].split("/")[0]
    _, owner_type = _resolve_owner(owner)
    projects = _list_projects(owner, owner_type)

    board_name = config["boards"][board_id].get("name", board_id)
    project = next((p for p in projects if p["title"] == board_name), None)
    if not project:
        raise GitHubError(f"Project '{board_name}' não encontrado")

    status_field = _get_status_field(project["id"])
    if not status_field:
        raise GitHubError(f"Campo Status não encontrado no project '{board_name}'")

    board_cache = {
        "project_id": project["id"],
        "project_number": project["number"],
        "status_field_id": status_field["id"],
        "options": {o["name"]: o["id"] for o in status_field.get("options", [])},
        "items": cache.get(board_id, {}).get("items", {}),
    }
    cache[board_id] = board_cache
    return board_cache


def fetch_board_items_graphql(project_id: str) -> list[dict]:
    """Busca todos os items de um project via GraphQL única.

    Retorna lista de dicts com: item_id, number, title, url, status, updated_at.
    Substitui gh project item-list (REST) por 1 query GraphQL.
    """
    query = """query($pid:ID!,$cursor:String){
      rateLimit{cost remaining resetAt}
      node(id:$pid){...on ProjectV2{
        items(first:100,after:$cursor){
          pageInfo{hasNextPage endCursor}
          nodes{
            id
            fieldValues(first:10){nodes{...on ProjectV2ItemFieldSingleSelectValue{field{...on ProjectV2SingleSelectField{name}} name}}}
            content{...on Issue{number title url updatedAt body}}
          }
        }
      }}
    }"""
    items = []
    cursor = ""
    while True:
        variables = {"pid": project_id}
        if cursor:
            variables["cursor"] = cursor
        data = _gql(query, **variables)
        rate = data.get("rateLimit", {})
        if rate:
            log.debug("[GitHub] GraphQL cost=%s remaining=%s resetAt=%s", rate.get("cost"), rate.get("remaining"), rate.get("resetAt"))
        node = data.get("node", {})
        page = node.get("items", {})
        for item in page.get("nodes", []):
            content = item.get("content")
            if not content or not content.get("number"):
                continue
            status_name = ""
            for fv in item.get("fieldValues", {}).get("nodes", []):
                if fv.get("field", {}).get("name") == "Status":
                    status_name = fv.get("name", "")
                    break
            items.append({
                "item_id": item["id"],
                "number": content["number"],
                "title": content["title"],
                "url": content.get("url", ""),
                "body": content.get("body", ""),
                "status": status_name,
                "updated_at": content.get("updatedAt", ""),
            })
        page_info = page.get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info["endCursor"]
    return items


def fetch_board_items(config: dict, cache: dict = None) -> dict[str, list[dict]]:
    """Busca items de todos os boards usando GraphQL e cache."""
    if cache is None:
        cache = {}
    result = {}
    for board_id in config["boards"]:
        try:
            meta = resolve_project_metadata(config, board_id, cache)
        except GitHubError:
            result[board_id] = []
            continue
        items = fetch_board_items_graphql(meta["project_id"])
        # Atualizar cache de items
        items_cache = meta.setdefault("items", {})
        for item in items:
            items_cache[str(item["number"])] = item["item_id"]
        result[board_id] = items
    return result


def fetch_issue_comments(repo: str, issue_number: int) -> dict:
    """Retorna {comments: [...], updatedAt: str}."""
    out = _gh("issue", "view", str(issue_number), "--repo", repo,
              "--json", "comments,updatedAt")
    return json.loads(out)


def fetch_issues_created_at(repo: str) -> dict[int, str]:
    """Retorna {number: createdAt} de todas as issues do repo."""
    out = _gh("issue", "list", "--repo", repo, "--state", "all",
              "--json", "number,createdAt", "--limit", "200")
    return {i["number"]: i["createdAt"] for i in json.loads(out)}


def fetch_updated_issues(repo: str, since: str) -> list[int]:
    """Retorna números das issues modificadas após a data de corte."""
    date_part = since[:10]
    out = _gh("issue", "list", "--repo", repo, "--state", "all",
              "--search", f"updated:>={date_part}",
              "--json", "number", "--limit", "200")
    return [i["number"] for i in json.loads(out)]


def push_boards(config: dict, desired: dict[str, list[str]]) -> dict:
    """Garante que os boards remotos tenham as colunas desejadas.

    Retorna metadata dict {board_id: {project_id, project_number, status_field_id, options}}
    para popular cache sem chamadas extras.
    """
    log.info("[GitHub] Checando — boards: %s", list(desired.keys()))
    owner = config["repo"].split("/")[0]
    owner_id, owner_type = _resolve_owner(owner)
    projects = _list_projects(owner, owner_type)
    projects_by_title = {p["title"]: p for p in projects}
    log.debug("[GitHub] Projects existentes: %s", list(projects_by_title.keys()))

    # Resolver projects existentes vs a criar
    board_projects = {}  # board_id → project dict
    for board_id in desired:
        board_name = config["boards"][board_id].get("name", board_id)
        project = projects_by_title.get(board_name)
        if not project:
            log.info("[GitHub] Board '%s' não encontrado — criando", board_name)
            project = _create_project(owner_id, board_name)
        else:
            log.debug("[GitHub] Board '%s' encontrado (id=%s)", board_name, project["id"])
        board_projects[board_id] = project

    # Batch: buscar Status de todos os projects em 1 query
    all_project_ids = [p["id"] for p in board_projects.values()]
    all_status = _get_all_status_fields(all_project_ids)

    metadata = {}
    for board_id, columns in desired.items():
        project = board_projects[board_id]
        board_name = config["boards"][board_id].get("name", board_id)
        status = all_status.get(project["id"])

        if not status:
            log.info("[GitHub] Board '%s' sem campo Status — criando com colunas: %s", board_name, columns)
            opts = "[" + ",".join(f'{{name:"{n}",color:GRAY,description:""}}' for n in columns) + "]"
            _gql(
                f'mutation($pid:ID!){{createProjectV2Field(input:{{projectId:$pid,dataType:SINGLE_SELECT,name:"Status",singleSelectOptions:{opts}}}){{projectV2Field{{...on ProjectV2SingleSelectField{{id}}}}}}}}',
                pid=project["id"],
            )
            # Re-buscar para obter id e options criados
            status = _get_status_field(project["id"])
        else:
            existing_by_name = {o["name"]: o["id"] for o in status.get("options", [])}

            ordered_opts = []
            for col in columns:
                opt = {"name": col}
                if col in existing_by_name:
                    opt["id"] = existing_by_name[col]
                ordered_opts.append(opt)

            removed = set(existing_by_name.keys()) - set(columns)
            if removed:
                log.info("[GitHub] Board '%s' — colunas a remover: %s", board_name, removed)

            needs_update = (
                [o["name"] for o in ordered_opts] != [o["name"] for o in status.get("options", [])]
            )
            if needs_update:
                log.info("[GitHub] Board '%s' — atualizando ordem/opções", board_name)
                _add_status_options(status["id"], ordered_opts)
            else:
                log.info("[GitHub] Board '%s' — sem alterações", board_name)

        # Montar metadata para cache
        if status:
            metadata[board_id] = {
                "project_id": project["id"],
                "project_number": project["number"],
                "status_field_id": status["id"],
                "options": {o["name"]: o["id"] for o in status.get("options", [])},
            }

    log.info("[GitHub] Concluído")
    return metadata


def add_issue_to_project(config: dict, board_id: str, issue_node_id: str, cache: dict = None) -> str:
    """Adiciona issue ao project via addProjectV2ItemById (idempotente).

    Retorna item_id. Atualiza cache se fornecido.
    """
    if cache is None:
        cache = {}
    meta = resolve_project_metadata(config, board_id, cache)
    project_id = meta["project_id"]

    _mutation_throttle()
    data = _gql(
        "mutation($pid:ID!,$nid:ID!){addProjectV2ItemById(input:{projectId:$pid,contentId:$nid}){item{id}}}",
        pid=project_id,
        nid=issue_node_id,
    )
    item_id = data["addProjectV2ItemById"]["item"]["id"]

    # Cachear — precisa do issue_number, extrair do node_id é impraticável
    # O caller deve cachear com o number correto
    return item_id


def get_issue_node_id(repo: str, issue_number: int) -> str:
    """Busca node_id (global ID) de uma issue via GraphQL."""
    owner, name = repo.split("/")
    data = _gql(
        "query($owner:String!,$name:String!,$num:Int!){repository(owner:$owner,name:$name){issue(number:$num){id}}}",
        owner=owner,
        name=name,
        num=int(issue_number),
    )
    issue = (data or {}).get("repository", {}) or {}
    issue = issue.get("issue")
    if not issue:
        raise GitHubError(f"Issue #{issue_number} não encontrada no repo {repo}")
    return issue["id"]


# ── Ações local → GitHub ──────────────────────────────────────────────────────


def create_issue(repo: str, title: str, body: str) -> int:
    """Cria issue no repo. Retorna o number."""
    out = _gh("issue", "create", "--repo", repo,
              "--title", title, "--body", body)
    # out é a URL da issue criada, ex: https://github.com/owner/repo/issues/42
    return int(out.strip().split("/")[-1])


def find_issue_by_title(repo: str, title: str) -> int | None:
    """Busca issue aberta com título exato. Retorna number ou None."""
    out = _gh("issue", "list", "--repo", repo, "--state", "open",
              "--search", f"in:title {title}", "--json", "number,title", "--limit", "50")
    for issue in json.loads(out):
        if issue["title"].strip() == title.strip():
            return issue["number"]
    return None


def close_issue(repo: str, issue_number: int) -> None:
    """Fecha uma issue."""
    _gh("issue", "close", str(issue_number), "--repo", repo)


def update_issue_body(repo: str, issue_number: int, body: str) -> None:
    """Atualiza o body de uma issue."""
    _gh("issue", "edit", str(issue_number), "--repo", repo, "--body", body)


def post_comment(repo: str, issue_number: int, body: str) -> None:
    """Posta um comentário na issue."""
    _gh("issue", "comment", str(issue_number), "--repo", repo, "--body", body)


def move_card(config: dict, issue_number: int, board_id: str, col_name: str, cache: dict = None) -> None:
    """Move issue para coluna no project board.

    Com cache: 1 mutation (updateProjectV2ItemFieldValue).
    Sem cache/item_id: addProjectV2ItemById + mutation.
    """
    if cache and cache.get(board_id):
        meta = cache[board_id]
    else:
        if cache is None:
            cache = {}
        meta = resolve_project_metadata(config, board_id, cache)

    project_id = meta["project_id"]
    field_id = meta["status_field_id"]
    option_id = meta["options"].get(col_name)
    if not option_id:
        # Cache stale — invalidar e rebuscar da fonte
        cache.pop(board_id, None)
        meta = resolve_project_metadata(config, board_id, cache)
        project_id = meta["project_id"]
        field_id = meta["status_field_id"]
        option_id = meta["options"].get(col_name)
        if not option_id:
            raise GitHubError(f"Coluna '{col_name}' não encontrada no project")

    items_cache = meta.setdefault("items", {})
    item_id = items_cache.get(str(issue_number))

    if not item_id:
        # Precisa adicionar ao project ou buscar item_id
        repo = config["repo"]
        node_id = get_issue_node_id(repo, issue_number)
        item_id = add_issue_to_project(config, board_id, node_id, cache)

    _mutation_throttle()
    _gql(
        "mutation($pid:ID!,$iid:ID!,$fid:ID!,$oid:String!){updateProjectV2ItemFieldValue(input:{projectId:$pid,itemId:$iid,fieldId:$fid,value:{singleSelectOptionId:$oid}}){projectV2Item{id}}}",
        pid=project_id,
        iid=item_id,
        fid=field_id,
        oid=option_id,
    )
