import time

from src.orchestrator import state as state_mod
from src.orchestrator import blocker, priority
from src.integrations import github, git
from src.integrations.github import sync_boards
from src.agents import run as agents_run, build_prompt as agents_build_prompt
from src.metrics import record as metrics_record, init_db
from src import logs


# ---------------------------------------------------------------------------
# Board helpers
# ---------------------------------------------------------------------------

def _boards(config: dict) -> dict:
    return config.get("boards", {})


def _find_column(config: dict, column_id: str) -> dict | None:
    for board in _boards(config).values():
        col = board.get("columns", {}).get(column_id)
        if col is not None:
            return col
    return None


def _column_name(config: dict, column_id: str) -> str:
    col = _find_column(config, column_id)
    return col.get("name", column_id) if col else column_id


def _advance(config: dict, column_id: str) -> str | None:
    col = _find_column(config, column_id)
    return col.get("change", {}).get("advance") if col else None


def _agent_for_column(config: dict, column_id: str) -> str | None:
    col = _find_column(config, column_id)
    return col.get("agent") if col else None


def _acao_for_column(config: dict, column_id: str) -> str | None:
    col = _find_column(config, column_id)
    return col.get("acao") if col else None


def _is_todo(config: dict, column_id: str) -> bool:
    for board in _boards(config).values():
        if board.get("todo") == column_id:
            return True
    return False


def _detect_column(config: dict, issue_labels: set[str]) -> str | None:
    """Retorna o id da coluna correspondente à label da issue, ou a coluna todo do primeiro board."""
    for board in _boards(config).values():
        for col_id in board.get("columns", {}):
            if col_id in issue_labels:
                return col_id
        return board.get("todo")
    return None


# ---------------------------------------------------------------------------
# run_once
# ---------------------------------------------------------------------------

def run_once(config: dict, sprint_issues: list[int] | None = None) -> None:
    if sprint_issues is None:
        sprint_issues = []

    current_state = state_mod.load()
    status = current_state["status"]

    # --- Gate: awaiting human approval ---
    if status == "awaiting_approval":
        # E5: issue fechada/deletada durante a espera → reseta state
        if not github.issue_exists(config, current_state["issue_number"]):
            logs.log_error(current_state["issue_number"], None, "issue não encontrada durante awaiting_approval — resetando state")
            _reset_state(current_state)
            state_mod.save(current_state)
            return

        approval = github.get_approval_status(config, current_state["issue_number"])
        if approval == "pending":
            return

        current_col = current_state.get("current_column")
        step = current_state.get("current_step", "unknown")
        logs.log_gate(current_state["issue_number"], step, approval)

        if approval == "approved":
            github.remove_label(config, current_state["issue_number"], "approved")
            next_col_id = _advance(config, current_col) if current_col else None
            next_col_cfg = _find_column(config, next_col_id) if next_col_id else None
            next_has_agent = next_col_cfg.get("agent") if next_col_cfg else False
            next_is_wait = next_col_cfg.get("wait_children") if next_col_cfg else False

            if next_col_id and (next_has_agent or next_is_wait):
                current_state["current_column"] = next_col_id
                current_state["current_step"] = next_has_agent or None
                current_state["status"] = "idle"
                current_state["rework"] = False
            else:
                _finish_issue(config, current_state, sprint_issues, next_col_id or "concluido")
            state_mod.save(current_state)
            return

        if approval == "rejected":
            github.remove_label(config, current_state["issue_number"], "rejected")
            current_state["rework"] = True
            current_state["status"] = "idle"
            state_mod.save(current_state)
            return

    # --- Normal execution ---
    if status == "idle":
        # E1: state corrompido com issue_number de issue inexistente
        if current_state.get("issue_number") and not github.issue_exists(config, current_state["issue_number"]):
            logs.log_error(current_state["issue_number"], None, "issue_number no state aponta para issue inexistente — resetando state")
            _reset_state(current_state)
            state_mod.save(current_state)
            return

        if current_state.get("current_feature") is None:
            if blocker.detect_deadlock(config):
                github.create_issue(
                    config,
                    title="[DEADLOCK] Ciclo de bloqueio detectado",
                    body="Todas as issues disponíveis estão bloqueadas. Intervenção humana necessária.",
                    labels=["needs-human"],
                )
                return
            issue = priority.select_next(config, current_state)
            if issue is None:
                return
            current_state["issue_number"] = issue["number"]
            current_state["current_feature"] = issue["title"]

            issue_labels = {l["name"] for l in issue.get("labels", [])}
            current_state["current_column"] = _detect_column(config, issue_labels)
            logs.log_issue_start(issue["number"], issue["title"])

    current_col = current_state.get("current_column")

    # Se está na coluna todo, avança automaticamente via advance
    if current_col and _is_todo(config, current_col):
        next_col_id = _advance(config, current_col)
        if next_col_id:
            github.move_card(config, current_state["issue_number"], _column_name(config, next_col_id))
            current_state["current_column"] = next_col_id
            current_col = next_col_id
            state_mod.save(current_state)
        else:
            return

    # Se a coluna aguarda filhos, verifica se todas estão concluídas
    col_cfg = _find_column(config, current_col) if current_col else None
    if col_cfg and col_cfg.get("wait_children") and not col_cfg.get("agent"):
        if blocker.all_children_done(config, current_state["issue_number"]):
            next_col_id = _advance(config, current_col)
            if next_col_id:
                github.move_card(config, current_state["issue_number"], _column_name(config, next_col_id))
                current_state["current_column"] = next_col_id
                current_col = next_col_id
                state_mod.save(current_state)
            else:
                _finish_issue(config, current_state, sprint_issues, current_col)
                state_mod.save(current_state)
        return  # aguarda próximo ciclo se filhos ainda pendentes

    role = _agent_for_column(config, current_col) if current_col else None
    if not role:
        return

    # Cria branch na primeira execução
    if current_state.get("current_step") is None:
        try:
            git.create_branch(config, current_state["current_feature"])
        except RuntimeError:
            pass

    issue = github.get_issue(config, current_state["issue_number"])
    acao = _acao_for_column(config, current_col)
    prompt = agents_build_prompt(
        role=role, issue=issue,
        rework=current_state.get("rework", False),
        acao=acao,
    )

    logs.log_agent_start(current_state["issue_number"], role, role)
    try:
        result = agents_run(role=role, context_files=[], prompt=prompt)
        logs.log_agent_end(
            current_state["issue_number"], role, role,
            result["duration_s"], result["tokens_in"], result["tokens_out"],
            current_state.get("rework", False),
            output=result["output"],
        )
    except Exception as exc:
        logs.log_error(current_state["issue_number"], role, str(exc))
        raise

    metrics_record(
        path=config.get("metrics_db", "metrics.db"),
        feature_id=str(current_state["issue_number"]),
        agent=role,
        duration_s=result["duration_s"],
        tokens_in=result["tokens_in"],
        tokens_out=result["tokens_out"],
        rework=current_state.get("rework", False),
    )

    col_name = _column_name(config, current_col)
    tokens_info = ""
    if result["tokens_in"] or result["tokens_out"]:
        tokens_info = f" | tokens: {result['tokens_in']}↑ {result['tokens_out']}↓"
    github.post_comment(
        config,
        current_state["issue_number"],
        body=f"✅ `{role}` concluído → `{col_name}` aguardando aprovação{tokens_info}",
    )
    github.move_card(config, current_state["issue_number"], col_name)

    current_state["current_step"] = role
    current_state["status"] = "awaiting_approval"
    current_state["rework"] = False
    state_mod.save(current_state)


def _reset_state(state: dict) -> None:
    state.update(status="idle", current_step=None, current_column=None,
                 current_feature=None, issue_number=None, rework=False)


def _finish_issue(config: dict, state: dict, sprint_issues: list[int], done_col_id: str) -> None:
    blocker.unblock_dependents(config, state["issue_number"])
    logs.log_issue_done(state["issue_number"])
    sprint_issues.append(state["issue_number"])
    github.move_card(config, state["issue_number"], _column_name(config, done_col_id))
    _reset_state(state)


# ---------------------------------------------------------------------------
# Optimizer + loop
# ---------------------------------------------------------------------------

def _run_optimizer(config: dict, sprint_issues: list[int]) -> None:
    logs.log_sprint_end(sprint_issues)
    prompt = (
        f"Sprint concluída. Issues processadas: {sprint_issues}.\n"
        "Analise os logs em logs/esteira.jsonl e as métricas em metrics.db.\n"
        "Identifique os principais problemas e proponha melhorias."
    )
    try:
        agents_run(role="optimizer", context_files=["logs/esteira.jsonl"], prompt=prompt)
    except Exception as exc:
        logs.log_error(None, "optimizer", str(exc))


def run_loop(config: dict, poll_interval_s: int = 60) -> None:
    init_db(config.get("metrics_db", "metrics.db"))
    sync_boards(config)
    sprint_issues: list[int] = []
    sprint_size = config.get("pipe", {}).get("sprint_size", 10)

    try:
        while True:
            run_once(config, sprint_issues)

            if len(sprint_issues) >= sprint_size:
                _run_optimizer(config, sprint_issues)
                sprint_issues = []

            sleep_s = (config.get("pipe", {}).get("sleeptime") or 1) * 60
            time.sleep(poll_interval_s if poll_interval_s != 60 else sleep_s)
    except KeyboardInterrupt:
        if sprint_issues:
            _run_optimizer(config, sprint_issues)
