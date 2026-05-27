import re

from src.integrations import github

_BLOCKING = {"blocked", "needs-human"}


def _labels(issue: dict) -> set[str]:
    return {l["name"] for l in issue.get("labels", [])}


def _is_blocked(issue: dict) -> bool:
    return bool(_BLOCKING & _labels(issue))


def _is_sub_issue(issue: dict) -> bool:
    """Sub-issue: body contains a #N reference to a parent issue."""
    body = issue.get("body") or ""
    return bool(re.search(r"#\d+", body))


def _oldest(issues: list[dict]) -> dict:
    return min(issues, key=lambda i: i.get("createdAt", ""))


def get_current_milestone(config: dict, state: dict) -> str | None:
    if state.get("current_milestone"):
        return state["current_milestone"]
    milestones = github.get_milestones(config)
    for ms in milestones:
        if github.get_issues(config, ms):
            return ms
    return None


def select_next(config: dict, state: dict) -> dict | None:
    milestone = get_current_milestone(config, state)
    if milestone is None:
        return None

    issues = github.get_issues(config, milestone)
    eligible = [i for i in issues if not _is_blocked(i)]

    if not eligible:
        # Try next milestone
        milestones = github.get_milestones(config)
        current_idx = milestones.index(milestone) if milestone in milestones else -1
        for ms in milestones[current_idx + 1:]:
            next_issues = [i for i in github.get_issues(config, ms) if not _is_blocked(i)]
            if next_issues:
                return _oldest(next_issues)
        return None

    # Level 1: sub-issues with in-progress
    l1 = [i for i in eligible if _is_sub_issue(i) and "in-progress" in _labels(i)]
    if l1:
        return _oldest(l1)

    # Level 2: sub-issues in backlog (no in-progress)
    l2 = [i for i in eligible if _is_sub_issue(i) and "in-progress" not in _labels(i)]
    if l2:
        return _oldest(l2)

    # Level 3: top-level milestone issues (no sub-issues pending)
    l3 = [i for i in eligible if not _is_sub_issue(i)]
    if l3:
        return _oldest(l3)

    return None
