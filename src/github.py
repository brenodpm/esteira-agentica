"""Integração com GitHub Projects V2 via gh CLI (GraphQL)."""

import json
import subprocess
import time

from src.log import log

_last_mutation_time = 0.0


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
        flag = "-F" if isinstance(v, (int, float, bool)) else "-f"
        args += [flag, f"{k}={v}"]
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
    _mutation_throttle()
    data = _gql(
        "mutation($ownerId:ID!,$title:String!){createProjectV2(input:{ownerId:$ownerId,title:$title}){projectV2{id number title}}}",
        ownerId=owner_id,
        title=title,
    )
    return data["createProjectV2"]["projectV2"]


def _add_status_options(field_id: str, options: list[dict]) -> None:
    """Atualiza opções do campo Status. options: [{name, id?}, ...] na ordem desejada."""
    log.info("[push_boards] Atualizando opções do field %s com: %s", field_id, [o["name"] for o in options])
    _mutation_throttle()
    parts = []
    for o in options:
        if o.get("id"):
            parts.append(f'{{id:"{o["id"]}",name:"{o["name"]}",color:GRAY,description:""}}')
        else:
            parts.append(f'{{name:"{o["name"]}",color:GRAY,description:""}}')
    opts = "[" + ",".join(parts) + "]"
    log.debug("[push_boards] Mutation payload: %s", opts)
    _gql(
        f'mutation($fid:ID!){{updateProjectV2Field(input:{{fieldId:$fid,singleSelectOptions:{opts}}}){{projectV2Field{{...on ProjectV2SingleSelectField{{id}}}}}}}}',
        fid=field_id,
    )
    log.info("[push_boards] Mutation executada com sucesso")


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


def push_boards(config: dict, desired: dict[str, list[str]]) -> None:
    """Garante que os boards remotos tenham as colunas desejadas."""
    log.info("[push_boards] Iniciando — boards: %s", list(desired.keys()))
    owner = config["repo"].split("/")[0]
    owner_id, owner_type = _resolve_owner(owner)
    projects = _list_projects(owner, owner_type)
    projects_by_title = {p["title"]: p for p in projects}
    log.debug("[push_boards] Projects existentes: %s", list(projects_by_title.keys()))

    for board_id, columns in desired.items():
        board_name = config["boards"][board_id].get("name", board_id)
        project = projects_by_title.get(board_name)
        if not project:
            log.info("[push_boards] Board '%s' não encontrado — criando", board_name)
            project = _create_project(owner_id, board_name)
        else:
            log.debug("[push_boards] Board '%s' encontrado (id=%s)", board_name, project["id"])

        status = _get_status_field(project["id"])
        if not status:
            log.info("[push_boards] Board '%s' sem campo Status — criando com colunas: %s", board_name, columns)
            opts = "[" + ",".join(f'{{name:"{n}",color:GRAY,description:""}}' for n in columns) + "]"
            _gql(
                f'mutation($pid:ID!){{createProjectV2Field(input:{{projectId:$pid,dataType:SINGLE_SELECT,name:"Status",singleSelectOptions:{opts}}}){{projectV2Field{{...on ProjectV2SingleSelectField{{id}}}}}}}}',
                pid=project["id"],
            )
        else:
            existing_by_name = {o["name"]: o["id"] for o in status.get("options", [])}
            log.info("[push_boards] Board '%s' — existentes: %s", board_name, set(existing_by_name.keys()))
            log.info("[push_boards] Board '%s' — desejadas: %s", board_name, columns)

            # Montar lista ordenada conforme pipe.yml, com IDs das existentes
            ordered_opts = []
            for col in columns:
                opt = {"name": col}
                if col in existing_by_name:
                    opt["id"] = existing_by_name[col]
                ordered_opts.append(opt)

            # Colunas no GitHub que não estão no pipe.yml serão removidas
            removed = set(existing_by_name.keys()) - set(columns)
            if removed:
                log.info("[push_boards] Board '%s' — colunas a remover: %s", board_name, removed)

            needs_update = (
                [o["name"] for o in ordered_opts] != [o["name"] for o in status.get("options", [])]
            )
            if needs_update:
                log.info("[push_boards] Board '%s' — atualizando ordem/opções", board_name)
                _add_status_options(status["id"], ordered_opts)
            else:
                log.info("[push_boards] Board '%s' — sem alterações", board_name)

    log.info("[push_boards] Concluído")


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
