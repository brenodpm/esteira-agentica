from src.integrations import github


def create_blocker(
    config: dict,
    blocked_issue: int,
    title: str,
    body: str,
    needs_human: bool = False,
) -> int:
    issue = github.create_issue(config, title=title, body=body, labels=[])
    new_number = issue["number"]
    github.add_label(config, blocked_issue, "blocked")
    if needs_human:
        github.add_label(config, new_number, "needs-human")
    return new_number


def unblock_dependents(config: dict, resolved_issue: int) -> list[int]:
    blocked = github.get_issues_with_label(config, "blocked")
    ref = f"#{resolved_issue}"
    unblocked = []
    for issue in blocked:
        if ref in (issue.get("body") or ""):
            num = issue["number"]
            github.remove_label(config, num, "blocked")
            github.move_card(config, num, "Backlog")
            unblocked.append(num)
    return unblocked


def detect_deadlock(config: dict) -> bool:
    next_issue = github.get_next_issue(config)
    if next_issue is not None:
        return False
    blocked = github.get_issues_with_label(config, "blocked")
    return len(blocked) > 0
