import re
import json
import subprocess

from src.integrations import github

_BLOCKING = {"blocked", "needs-human"}


def _labels(issue: dict) -> set[str]:
    return {l["name"] for l in issue.get("labels", [])}


def _is_blocked(issue: dict) -> bool:
    return bool(_BLOCKING & _labels(issue))


def _is_sub_issue(issue: dict) -> bool:
    body = issue.get("body") or ""
    return bool(re.search(r"#\d+", body))


def _oldest(issues: list[dict]) -> dict:
    return min(issues, key=lambda i: i.get("createdAt", ""))


def _gh_issues(repo: str) -> list[dict]:
    result = subprocess.run(
        ["gh", "issue", "list", "--repo", repo, "--state", "open",
         "--json", "number,title,labels,createdAt,body", "--limit", "100"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def _board_agent_col_ids(board: dict) -> set[str]:
    return {col_id for col_id, col in board.get("columns", {}).items() if col.get("agent")}


def _todo_col_id(board: dict) -> str:
    return board.get("todo", "backlog")


def _all_col_ids(board: dict) -> set[str]:
    return set(board.get("columns", {}).keys())


def _terminal_col_ids(board: dict) -> set[str]:
    """Colunas sem 'change' — estados terminais (concluído, cancelado)."""
    return {col_id for col_id, col in board.get("columns", {}).items() if not col.get("change")}


def _eligible_for_board(issues: list[dict], board: dict) -> list[dict]:
    """Issues elegíveis para um board: não bloqueadas, não em coluna terminal (sem 'change'),
    com label do todo, de coluna com agent, ou sem nenhuma label de coluna conhecida (→ todo)."""
    todo = _todo_col_id(board)
    agent_cols = _board_agent_col_ids(board)
    all_cols = _all_col_ids(board)
    terminal = _terminal_col_ids(board)
    result = []
    for i in issues:
        if _is_blocked(i):
            continue
        lbls = _labels(i)
        col_labels = lbls & all_cols
        if col_labels & terminal:
            continue
        if col_labels & ({todo} | agent_cols) or not col_labels:
            result.append(i)
    return result


def _pick_from(issues: list[dict], board: dict) -> dict | None:
    """Dentro de um board, prioriza colunas com agent > sub-issues > top-level."""
    agent_cols = _board_agent_col_ids(board)

    l1 = [i for i in issues if _labels(i) & agent_cols]
    if l1:
        return _oldest(l1)

    l2 = [i for i in issues if _is_sub_issue(i)]
    if l2:
        return _oldest(l2)

    if issues:
        return _oldest(issues)

    return None


def select_next(config: dict, state: dict, exclude: set[int] | None = None) -> dict | None:
    """Seleciona a próxima issue a ser processada.

    Boards são agrupados por priority (menor = maior prioridade).
    Só avança ao próximo grupo quando não há issues elegíveis no atual.
    Quando não há boards configurados, cai no modo legado (milestone).
    """
    boards = config.get("boards", {})

    if boards:
        return _select_from_board(config, exclude=exclude)
    else:
        return _select_from_milestone(config, state)


def _select_from_board(config: dict, exclude: set[int] | None = None) -> dict | None:
    boards = config.get("boards", {})
    all_issues = _gh_issues(config["repo"])
    if exclude:
        all_issues = [i for i in all_issues if i["number"] not in exclude]

    # Agrupa boards por priority e ordena do menor para o maior
    groups: dict[int, list[dict]] = {}
    for board in boards.values():
        p = board.get("priority", 0)
        groups.setdefault(p, []).append(board)

    for priority in sorted(groups):
        candidates = []
        for board in groups[priority]:
            eligible = _eligible_for_board(all_issues, board)
            pick = _pick_from(eligible, board)
            if pick:
                candidates.append(pick)

        if candidates:
            return _oldest(candidates)

    return None


def _select_from_milestone(config: dict, state: dict) -> dict | None:
    """Modo legado: busca por milestone."""
    milestone = get_current_milestone(config, state)
    if milestone is None:
        return None

    issues = github.get_issues(config, milestone)
    eligible = [i for i in issues if not _is_blocked(i)]

    if not eligible:
        milestones = github.get_milestones(config)
        current_idx = milestones.index(milestone) if milestone in milestones else -1
        for ms in milestones[current_idx + 1:]:
            next_issues = [i for i in github.get_issues(config, ms) if not _is_blocked(i)]
            if next_issues:
                return _oldest(next_issues)
        return None

    l1 = [i for i in eligible if _is_sub_issue(i) and "in-progress" in _labels(i)]
    if l1:
        return _oldest(l1)

    l2 = [i for i in eligible if _is_sub_issue(i) and "in-progress" not in _labels(i)]
    if l2:
        return _oldest(l2)

    l3 = [i for i in eligible if not _is_sub_issue(i)]
    if l3:
        return _oldest(l3)

    return None


def get_current_milestone(config: dict, state: dict) -> str | None:
    if state.get("current_milestone"):
        return state["current_milestone"]
    milestones = github.get_milestones(config)
    for ms in milestones:
        if github.get_issues(config, ms):
            return ms
    return None
