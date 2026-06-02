import re

from src.integrations import github

# ---------------------------------------------------------------------------
# Body parsing — vínculo pai/filho
# ---------------------------------------------------------------------------

def parse_sub_tasks(body: str) -> list[int]:
    """Extrai números de issues listadas em ## Sub-tasks no body.

    Formato esperado:
        ## Sub-tasks
        - [ ] #12
        - [x] #13
    Retorna lista de ints independente do estado do checkbox.
    """
    numbers = []
    in_section = False
    for line in (body or "").splitlines():
        if re.match(r"^#+\s*sub.?tasks?", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section:
            if line.startswith("#"):
                break  # nova seção
            m = re.search(r"#(\d+)", line)
            if m:
                numbers.append(int(m.group(1)))
    return numbers


def parse_parent(body: str) -> int | None:
    """Extrai o número da issue pai do body.

    Formato esperado (qualquer lugar no body):
        Parent: #5
    """
    m = re.search(r"^\s*[Pp]arent\s*:\s*#(\d+)", body or "", re.MULTILINE)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# Blocker helpers
# ---------------------------------------------------------------------------

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


def all_children_done(config: dict, issue_number: int) -> bool:
    """Retorna True se todas as sub-tasks listadas no body da issue estão fechadas."""
    issue = github.get_issue(config, issue_number)
    children = parse_sub_tasks(issue.get("body") or "")
    if not children:
        return True
    for child_num in children:
        child = github.get_issue(config, child_num)
        if child.get("state", "open") != "closed":
            return False
    return True
