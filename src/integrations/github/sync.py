"""Sincroniza boards/colunas do esteira.yml com GitHub Projects V2 via GraphQL."""

import json
import subprocess


def _gql(query: str, **variables) -> dict:
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        args += ["-f", f"{k}={v}"]
    result = subprocess.run(args, capture_output=True, text=True)
    if not result.stdout:
        raise RuntimeError(result.stderr.strip())
    data = json.loads(result.stdout)
    # Erros parciais (ex: org não encontrada mas user existe) são tolerados
    if "errors" in data and "data" not in data:
        raise RuntimeError(data["errors"])
    return data.get("data", {})


def _owner_id(owner: str) -> tuple[str, str]:
    """Retorna (node_id, type) onde type é 'user' ou 'organization'."""
    data = _gql(
        "query($login:String!){organization(login:$login){id} user(login:$login){id}}",
        login=owner,
    )
    if data.get("organization") and data["organization"].get("id"):
        return data["organization"]["id"], "organization"
    return data["user"]["id"], "user"


def _list_projects(owner: str, owner_type: str) -> list[dict]:
    """Retorna lista de {number, id, title} dos projetos do owner."""
    if owner_type == "organization":
        query = "query($login:String!){organization(login:$login){projectsV2(first:50){nodes{id number title}}}}"
        data = _gql(query, login=owner)
        return data["organization"]["projectsV2"]["nodes"]
    else:
        query = "query($login:String!){user(login:$login){projectsV2(first:50){nodes{id number title}}}}"
        data = _gql(query, login=owner)
        return data["user"]["projectsV2"]["nodes"]


def _create_project(owner_id: str, title: str) -> dict:
    """Cria projeto e retorna {id, number, title}."""
    data = _gql(
        "mutation($ownerId:ID!,$title:String!){createProjectV2(input:{ownerId:$ownerId,title:$title}){projectV2{id number title}}}",
        ownerId=owner_id,
        title=title,
    )
    return data["createProjectV2"]["projectV2"]


def _get_status_field(project_id: str) -> dict | None:
    """Retorna o campo Status do projeto ou None."""
    data = _gql(
        "query($id:ID!){node(id:$id){...on ProjectV2{fields(first:20){nodes{...on ProjectV2SingleSelectField{id name options{id name}}}}}}}",
        id=project_id,
    )
    for field in data["node"]["fields"]["nodes"]:
        if field.get("name") == "Status":
            return field
    return None


def _create_status_field(project_id: str) -> dict:
    """Cria campo Status e retorna {id, options:[]}."""
    data = _gql(
        "mutation($pid:ID!){createProjectV2Field(input:{projectId:$pid,dataType:SINGLE_SELECT,name:\"Status\",singleSelectOptions:[{name:\"Backlog\",color:GRAY,description:\"\"}]}){projectV2Field{...on ProjectV2SingleSelectField{id name options{id name}}}}}",
        pid=project_id,
    )
    return data["createProjectV2Field"]["projectV2Field"]


def _add_status_option(field_id: str, existing_options: list[str], option_name: str) -> None:
    """Adiciona uma opção ao campo Status reenviando todas as opções existentes + a nova."""
    all_options = existing_options + [option_name]
    opts_gql = "[" + ",".join(f'{{name:"{n}",color:GRAY,description:""}}' for n in all_options) + "]"
    _gql(
        f'mutation($fid:ID!){{updateProjectV2Field(input:{{fieldId:$fid,singleSelectOptions:{opts_gql}}}){{projectV2Field{{...on ProjectV2SingleSelectField{{id}}}}}}}}',
        fid=field_id,
    )


def sync_boards(config: dict) -> None:
    """Sincroniza todos os boards do esteira.yml com GitHub Projects V2.

    Para cada board:
    - Cria o projeto se não existir
    - Cria o campo Status se não existir
    - Adiciona opções (colunas) ausentes — nunca remove existentes
    """
    owner = config["repo"].split("/")[0]
    boards = config.get("boards", {})

    if not boards:
        print("Nenhum board configurado em esteira.yml.")
        return

    try:
        owner_id, owner_type = _owner_id(owner)
    except Exception as e:
        raise RuntimeError(f"Não foi possível resolver owner '{owner}': {e}") from e

    existing_projects = _list_projects(owner, owner_type)
    projects_by_name = {p["title"]: p for p in existing_projects}

    for board_id, board in boards.items():
        board_name = board.get("name", board_id)
        columns = board.get("columns", {})

        # Garante projeto
        if board_name in projects_by_name:
            project = projects_by_name[board_name]
            print(f"  [ok] projeto '{board_name}' já existe (#{project['number']})")
        else:
            project = _create_project(owner_id, board_name)
            print(f"  [+] projeto '{board_name}' criado (#{project['number']})")

        project_id = project["id"]

        # Garante campo Status
        status_field = _get_status_field(project_id)
        if status_field is None:
            status_field = _create_status_field(project_id)
            print(f"      [+] campo 'Status' criado em '{board_name}'")
        else:
            print(f"      [ok] campo 'Status' já existe em '{board_name}'")

        field_id = status_field["id"]
        existing_options = {o["name"] for o in status_field.get("options", [])}

        # Garante opções (colunas)
        for col_id, col in columns.items():
            col_name = col.get("name", col_id)
            if col_name not in existing_options:
                _add_status_option(field_id, list(existing_options), col_name)
                existing_options.add(col_name)
                print(f"      [+] coluna '{col_name}' adicionada")
            else:
                print(f"      [ok] coluna '{col_name}' já existe")
