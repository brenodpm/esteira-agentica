"""Integração com GitHub Projects V2 via gh CLI (GraphQL)."""

import json
import subprocess

from src.log import log


class GitHubError(Exception):
    """Erro genérico de comunicação com GitHub."""


class RateLimitError(GitHubError):
    """Rate limit atingido."""


def _gh(*args) -> str:
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    output = result.stdout.strip()
    error = result.stderr.strip()

    if "rate limit" in output.lower() or "rate limit" in error.lower():
        log.warning("Rate limit na chamada: gh %s", " ".join(args[:3]))
        raise RateLimitError("GitHub API rate limit excedido")

    if result.returncode != 0:
        log.debug("gh %s → erro: %s", " ".join(args[:3]), error or output)
        raise GitHubError(error or output or f"gh retornou código {result.returncode}")

    return result.stdout


def _gql(query: str, **variables) -> dict:
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        args += ["-f", f"{k}={v}"]
    result = subprocess.run(args, capture_output=True, text=True)
    output = result.stdout.strip()
    error = result.stderr.strip()

    if "rate limit" in output.lower() or "rate limit" in error.lower():
        raise RateLimitError("GitHub API rate limit excedido")

    if not output:
        raise GitHubError(error or "Resposta vazia do GraphQL")

    data = json.loads(output)
    if "errors" in data and "data" not in data:
        raise GitHubError(str(data["errors"]))
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


def _create_project(owner_id: str, title: str) -> dict:
    data = _gql(
        "mutation($ownerId:ID!,$title:String!){createProjectV2(input:{ownerId:$ownerId,title:$title}){projectV2{id number title}}}",
        ownerId=owner_id,
        title=title,
    )
    return data["createProjectV2"]["projectV2"]


def _add_status_options(field_id: str, all_options: list[str]) -> None:
    opts = "[" + ",".join(f'{{name:"{n}",color:GRAY,description:""}}' for n in all_options) + "]"
    _gql(
        f'mutation($fid:ID!){{updateProjectV2Field(input:{{fieldId:$fid,singleSelectOptions:{opts}}}){{projectV2Field{{...on ProjectV2SingleSelectField{{id}}}}}}}}',
        fid=field_id,
    )


def fetch_board_items(config: dict) -> dict[str, list[dict]]:
    """Busca items de todos os boards."""
    owner = config["repo"].split("/")[0]
    _, owner_type = _resolve_owner(owner)
    projects = _list_projects(owner, owner_type)
    projects_by_title = {p["title"]: p for p in projects}

    result = {}
    for board_id, board in config["boards"].items():
        board_name = board.get("name", board_id)
        project = projects_by_title.get(board_name)
        if not project:
            result[board_id] = []
            continue
        out = _gh("project", "item-list", str(project["number"]),
                  "--owner", owner, "--format", "json", "--limit", "200")
        data = json.loads(out)
        items = []
        for item in data.get("items", []):
            content = item.get("content", {})
            if content.get("type") != "Issue":
                continue
            items.append({
                "number": content["number"],
                "title": content["title"],
                "body": content.get("body", ""),
                "status": item.get("status", ""),
                "url": content.get("url", ""),
            })
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


def push_boards(config: dict, desired: dict[str, list[str]]) -> None:
    """Garante que os boards remotos tenham as colunas desejadas."""
    owner = config["repo"].split("/")[0]
    owner_id, owner_type = _resolve_owner(owner)
    projects = _list_projects(owner, owner_type)
    projects_by_title = {p["title"]: p for p in projects}

    for board_id, columns in desired.items():
        board_name = config["boards"][board_id].get("name", board_id)
        project = projects_by_title.get(board_name)
        if not project:
            project = _create_project(owner_id, board_name)

        status = _get_status_field(project["id"])
        if not status:
            opts = "[" + ",".join(f'{{name:"{n}",color:GRAY,description:""}}' for n in columns) + "]"
            _gql(
                f'mutation($pid:ID!){{createProjectV2Field(input:{{projectId:$pid,dataType:SINGLE_SELECT,name:"Status",singleSelectOptions:{opts}}}){{projectV2Field{{...on ProjectV2SingleSelectField{{id}}}}}}}}',
                pid=project["id"],
            )
        else:
            existing = {o["name"] for o in status.get("options", [])}
            all_opts = list(existing)
            for col in columns:
                if col not in existing:
                    all_opts.append(col)
            if len(all_opts) > len(existing):
                _add_status_options(status["id"], all_opts)


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


def move_card(config: dict, issue_number: int, board_id: str, col_name: str) -> None:
    """Move issue para coluna no project board."""
    owner = config["repo"].split("/")[0]
    repo = config["repo"]
    _, owner_type = _resolve_owner(owner)
    projects = _list_projects(owner, owner_type)

    board_name = config["boards"][board_id].get("name", board_id)
    project = next((p for p in projects if p["title"] == board_name), None)
    if not project:
        raise GitHubError(f"Project '{board_name}' não encontrado")

    project_number = str(project["number"])
    project_id = project["id"]
    issue_url = f"https://github.com/{repo}/issues/{issue_number}"

    # Busca item no project
    out = _gh("project", "item-list", project_number,
              "--owner", owner, "--format", "json", "--limit", "200")
    items = json.loads(out).get("items", [])
    item_id = None
    for item in items:
        content = item.get("content", {})
        if content.get("url") == issue_url:
            item_id = item["id"]
            break

    # Se não está no project, adiciona
    if not item_id:
        _gh("project", "item-add", project_number, "--owner", owner, "--url", issue_url)
        out = _gh("project", "item-list", project_number,
                  "--owner", owner, "--format", "json", "--limit", "200")
        items = json.loads(out).get("items", [])
        for item in items:
            content = item.get("content", {})
            if content.get("url") == issue_url:
                item_id = item["id"]
                break

    if not item_id:
        raise GitHubError(f"Não foi possível adicionar issue #{issue_number} ao project")

    # Busca campo Status e opção
    status_field = _get_status_field(project_id)
    if not status_field:
        raise GitHubError("Campo Status não encontrado no project")

    option = next((o for o in status_field.get("options", []) if o["name"] == col_name), None)
    if not option:
        raise GitHubError(f"Coluna '{col_name}' não encontrada no project")

    _gql(
        "mutation($pid:ID!,$iid:ID!,$fid:ID!,$oid:String!){updateProjectV2ItemFieldValue(input:{projectId:$pid,itemId:$iid,fieldId:$fid,value:{singleSelectOptionId:$oid}}){projectV2Item{id}}}",
        pid=project_id,
        iid=item_id,
        fid=status_field["id"],
        oid=option["id"],
    )
