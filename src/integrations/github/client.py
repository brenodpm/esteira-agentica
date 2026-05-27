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


def move_card(config: dict, issue_number: int, column: str) -> None:
    repo = config["repo"]
    _gh("project", "item-edit", "--repo", repo, "--field-value", column,
        "--id", str(issue_number))


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
