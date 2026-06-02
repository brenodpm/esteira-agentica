import json
import subprocess


def _gh(*args) -> str:
    try:
        result = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.stderr) from e


_BLOCKING_LABELS = {"blocked", "needs-human"}


def get_next_issue(config: dict) -> dict | None:
    repo = config["repo"]
    out = _gh("issue", "list", "--repo", repo, "--state", "open", "--json",
              "number,title,labels,createdAt", "--limit", "100")
    issues = json.loads(out)
    eligible = [
        i for i in issues
        if not _BLOCKING_LABELS.intersection(l["name"] for l in i.get("labels", []))
    ]
    if not eligible:
        return None
    return min(eligible, key=lambda i: i["createdAt"])


def get_issue(config: dict, issue_number: int) -> dict:
    repo = config["repo"]
    out = _gh("issue", "view", str(issue_number), "--repo", repo, "--json",
              "number,title,body,labels,state,createdAt")
    return json.loads(out)


def post_comment(config: dict, issue_number: int, body: str) -> None:
    repo = config["repo"]
    _gh("issue", "comment", str(issue_number), "--repo", repo, "--body", body)


def add_label(config: dict, issue_number: int, label: str) -> None:
    repo = config["repo"]
    _gh("issue", "edit", str(issue_number), "--repo", repo, "--add-label", label)


def remove_label(config: dict, issue_number: int, label: str) -> None:
    repo = config["repo"]
    _gh("issue", "edit", str(issue_number), "--repo", repo, "--remove-label", label)


def _get_projects(owner: str) -> list[dict]:
    """Retorna lista de {number, id, title} dos projetos do owner."""
    out = _gh("project", "list", "--owner", owner, "--format", "json",
              "--jq", ".projects[] | {number, id, title}")
    projects = []
    for line in out.strip().splitlines():
        line = line.strip()
        if line:
            projects.append(json.loads(line))
    return projects


def _find_project_for_board(config: dict, column_name: str) -> dict | None:
    """Retorna o projeto (number + id) que contém a coluna com o nome dado."""
    owner = config["repo"].split("/")[0]
    projects = _get_projects(owner)
    projects_by_title = {p["title"]: p for p in projects}

    for board in config.get("boards", {}).values():
        board_name = board.get("name", "")
        for col in board.get("columns", {}).values():
            if col.get("name") == column_name:
                return projects_by_title.get(board_name)
    return None


def move_card(config: dict, issue_number: int, column_name: str) -> None:
    """Move issue para coluna do board pelo nome da coluna definido em esteira.yml."""
    owner = config["repo"].split("/")[0]
    project = _find_project_for_board(config, column_name)
    if not project:
        return

    project_number = str(project["number"])
    project_id = project["id"]
    repo = config["repo"]
    issue_url = f"https://github.com/{repo}/issues/{issue_number}"

    try:
        item_id = _gh("project", "item-list", project_number,
                      "--owner", owner, "--format", "json",
                      "--jq", f'.items[] | select(.content.url=="{issue_url}") | .id').strip()
        if not item_id:
            _gh("project", "item-add", project_number, "--owner", owner, "--url", issue_url)
            item_id = _gh("project", "item-list", project_number,
                          "--owner", owner, "--format", "json",
                          "--jq", f'.items[] | select(.content.url=="{issue_url}") | .id').strip()
    except RuntimeError:
        return

    if not item_id:
        return

    try:
        field_info = _gh("project", "field-list", project_number,
                         "--owner", owner, "--format", "json",
                         "--jq", '.fields[] | select(.name=="Status") | {id: .id, options: .options}')
        if not field_info.strip():
            return
        field = json.loads(field_info)
        field_id = field["id"]
        option = next((o for o in field.get("options", []) if o["name"] == column_name), None)
        if not option:
            return
        _gh("project", "item-edit", "--id", item_id,
            "--field-id", field_id, "--project-id", project_id,
            "--single-select-option-id", option["id"])
    except (RuntimeError, StopIteration, json.JSONDecodeError, KeyError):
        return


def open_pr(config: dict, title: str, body: str, head: str, base: str) -> dict:
    repo = config["repo"]
    out = _gh("pr", "create", "--repo", repo, "--title", title, "--body", body,
              "--head", head, "--base", base, "--json", "number,url,title")
    return json.loads(out)


def create_issue(config: dict, title: str, body: str, labels: list[str]) -> dict:
    repo = config["repo"]
    args = ["issue", "create", "--repo", repo, "--title", title, "--body", body]
    for label in labels:
        args += ["--label", label]
    args += ["--json", "number,url,title"]
    out = _gh(*args)
    return json.loads(out)


def issue_exists(config: dict, issue_number: int) -> bool:
    try:
        get_issue(config, issue_number)
        return True
    except RuntimeError:
        return False


def get_approval_status(config: dict, issue_number: int) -> str:
    issue = get_issue(config, issue_number)
    label_names = {l["name"] for l in issue.get("labels", [])}
    if "approved" in label_names:
        return "approved"
    if "rejected" in label_names:
        return "rejected"
    return "pending"


def get_issues_with_label(config: dict, label: str) -> list[dict]:
    repo = config["repo"]
    out = _gh("issue", "list", "--repo", repo, "--state", "open",
              "--label", label, "--json", "number,title,body", "--limit", "100")
    return json.loads(out)


def get_milestones(config: dict) -> list[str]:
    repo = config["repo"]
    out = _gh("api", f"repos/{repo}/milestones", "--jq", "[.[].title]")
    return json.loads(out)


def get_issues(config: dict, milestone: str) -> list[dict]:
    repo = config["repo"]
    out = _gh("issue", "list", "--repo", repo, "--state", "open",
              "--milestone", milestone,
              "--json", "number,title,labels,createdAt,body", "--limit", "100")
    return json.loads(out)
