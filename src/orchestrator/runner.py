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


def _git_merge_pr(config: dict, branch: str) -> None:
    """Faz merge do PR aberto para a branch via gh."""
    import subprocess
    repo = config["repo"]
    result = subprocess.run(
        ["gh", "pr", "merge", "--repo", repo, "--merge", "--delete-branch", branch],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())


def _find_column(config: dict, column_id: str, board_key: str | None = None) -> dict | None:
    for bk, board in _boards(config).items():
        if board_key and bk != board_key:
            continue
        col = board.get("columns", {}).get(column_id)
        if col is not None:
            return col
    return None


def _find_board_for_column(config: dict, column_id: str, board_key: str | None = None) -> dict | None:
    for bk, board in _boards(config).items():
        if board_key and bk != board_key:
            continue
        if column_id in board.get("columns", {}):
            return board
    return None


def _board_name_for_column(config: dict, column_id: str, board_key: str | None = None) -> str | None:
    board = _find_board_for_column(config, column_id, board_key)
    return board.get("name") if board else None


def _flow_config(config: dict, column_id: str, board_key: str | None = None) -> dict:
    """Retorna o dict do flow (create, merge, prefix) para a coluna, ou defaults."""
    board = _find_board_for_column(config, column_id, board_key)
    flow_key = board.get("flow", "feature") if board else "feature"
    flow = config.get("git", {}).get("flow", {})
    return flow.get(flow_key, {"create": "main", "merge": "main", "prefix": flow_key})


def _column_name(config: dict, column_id: str, board_key: str | None = None) -> str:
    col = _find_column(config, column_id, board_key)
    return col.get("name", column_id) if col else column_id


def _advance(config: dict, column_id: str, board_key: str | None = None) -> str | None:
    col = _find_column(config, column_id, board_key)
    return col.get("change", {}).get("advance") if col else None


def _agent_for_column(config: dict, column_id: str, board_key: str | None = None) -> str | None:
    col = _find_column(config, column_id, board_key)
    return col.get("agent") if col else None


def _acao_for_column(config: dict, column_id: str, board_key: str | None = None) -> str | None:
    col = _find_column(config, column_id, board_key)
    return col.get("acao") if col else None


def _git_commit_flag(config: dict, column_id: str, board_key: str | None = None) -> bool:
    col = _find_column(config, column_id, board_key)
    return bool(col.get("git_commit")) if col else False


def _git_merge_flag(config: dict, column_id: str, board_key: str | None = None) -> bool:
    col = _find_column(config, column_id, board_key)
    return bool(col.get("git_merge")) if col else False


def _is_todo(config: dict, column_id: str, board_key: str | None = None) -> bool:
    for bk, board in _boards(config).items():
        if board_key and bk != board_key:
            continue
        if board.get("todo") == column_id:
            return True
    return False


def _detect_board(config: dict, issue_labels: set[str]) -> tuple[str, str] | tuple[None, None]:
    """Retorna (board_key, col_id) para a issue.

    Prioridade:
    1. Label igual ao id de uma coluna específica (ex: 'correcao')
    2. Label igual ao board_key (ex: 'bug') → todo desse board
    3. Fallback: todo do board de maior prioridade
    """
    # 1. label bate com col_id em algum board
    for bk, board in _boards(config).items():
        for col_id in board.get("columns", {}):
            if col_id in issue_labels:
                return bk, col_id

    # 2. label bate com board key
    for bk, board in _boards(config).items():
        if bk in issue_labels or board.get("name", "").lower() in issue_labels:
            todo = board.get("todo")
            return bk, todo

    # 3. fallback: board de maior prioridade
    best_bk, best_board = max(_boards(config).items(), key=lambda kv: kv[1].get("priority", 0))
    return best_bk, best_board.get("todo")


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
        current_board = current_state.get("current_board")
        step = current_state.get("current_step", "unknown")
        logs.log_gate(current_state["issue_number"], step, approval)

        if approval == "approved":
            github.remove_label(config, current_state["issue_number"], "approved")

            # merge + delete branch quando a coluna tem git_merge=true
            if current_col and _git_merge_flag(config, current_col, current_board):
                try:
                    branch = git.current_branch()
                    _git_merge_pr(config, branch)
                    git.delete_branch(branch)
                except RuntimeError as e:
                    logs.log_error(current_state["issue_number"], None, f"merge/delete branch falhou: {e}")

            next_col_id = _advance(config, current_col, current_board) if current_col else None
            next_col_cfg = _find_column(config, next_col_id, current_board) if next_col_id else None
            next_has_agent = next_col_cfg.get("agent") if next_col_cfg else False
            next_is_wait = next_col_cfg.get("wait_children") if next_col_cfg else False
            next_is_terminal = not next_col_cfg or (not next_has_agent and not next_is_wait and not _advance(config, next_col_id))

            if next_col_id and (next_has_agent or next_is_wait):
                current_state["current_column"] = next_col_id
                current_state["current_step"] = next_has_agent or None
                current_state["status"] = "idle"
                current_state["rework"] = False
            elif next_col_id and not next_is_terminal:
                # coluna de gate humano: sem agente, mas tem avanço — move e aguarda aprovação
                github.move_card(config, current_state["issue_number"], _column_name(config, next_col_id), _board_name_for_column(config, next_col_id))
                current_state["current_column"] = next_col_id
                current_state["current_step"] = None
                current_state["status"] = "awaiting_approval"
                current_state["rework"] = False
            else:
                _finish_issue(config, current_state, sprint_issues, next_col_id or "concluido", current_board)
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
            board_key, col_id = _detect_board(config, issue_labels)
            current_state["current_board"] = board_key
            current_state["current_column"] = col_id
            logs.log_info(issue["number"], None, f"board detectado: '{board_key}' → coluna '{col_id}'")
            logs.log_issue_start(issue["number"], issue["title"])
        elif current_state.get("current_board") is None and current_state.get("issue_number"):
            # Primeira vez retomando issue sem board detectado — detecta agora
            issue = github.get_issue(config, current_state["issue_number"])
            issue_labels = {l["name"] for l in issue.get("labels", [])}
            board_key, col_id = _detect_board(config, issue_labels)
            logs.log_info(current_state["issue_number"], None,
                          f"board detectado (retomada): '{board_key}' → coluna '{col_id}'")
            current_state["current_board"] = board_key
            current_state["current_column"] = col_id
            state_mod.save(current_state)

    current_col = current_state.get("current_column")
    current_board = current_state.get("current_board")

    # Se está na coluna todo, avança automaticamente via advance
    if current_col and _is_todo(config, current_col, current_board):
        next_col_id = _advance(config, current_col, current_board)
        if next_col_id:
            github.move_card(config, current_state["issue_number"], _column_name(config, next_col_id, current_board), _board_name_for_column(config, next_col_id, current_board))
            current_state["current_column"] = next_col_id
            current_col = next_col_id
            state_mod.save(current_state)
        else:
            return

    # Se a coluna aguarda filhos, verifica se todas estão concluídas
    col_cfg = _find_column(config, current_col, current_board) if current_col else None
    if col_cfg and col_cfg.get("wait_children") and not col_cfg.get("agent"):
        if blocker.all_children_done(config, current_state["issue_number"]):
            next_col_id = _advance(config, current_col, current_board)
            if next_col_id:
                github.move_card(config, current_state["issue_number"], _column_name(config, next_col_id, current_board), _board_name_for_column(config, next_col_id, current_board))
                current_state["current_column"] = next_col_id
                current_col = next_col_id
                state_mod.save(current_state)
            else:
                _finish_issue(config, current_state, sprint_issues, current_col)
                state_mod.save(current_state)
        return  # aguarda próximo ciclo se filhos ainda pendentes

    role = _agent_for_column(config, current_col, current_board) if current_col else None
    if not role:
        return

    # Cria branch na primeira execução usando create do flow do board
    if current_state.get("current_step") is None:
        flow = _flow_config(config, current_col, current_board)
        board = _find_board_for_column(config, current_col, current_board)
        flow_key = board.get("flow", "feature") if board else "feature"
        try:
            git.create_branch(config, current_state["current_feature"], flow_key=flow_key)
        except RuntimeError:
            pass

    issue = github.get_issue(config, current_state["issue_number"])
    acao = _acao_for_column(config, current_col, current_board)
    prompt = agents_build_prompt(
        role=role, issue=issue,
        rework=current_state.get("rework", False),
        acao=acao,
    )

    logs.log_agent_start(current_state["issue_number"], role, role)
    try:
        result = agents_run(role=role, context_files=[], prompt=prompt)
        run_name = f"#{current_state['issue_number']} {current_state.get('current_feature', '')} / {role}"
        logs.log_agent_end(
            current_state["issue_number"], role, role,
            result["duration_s"], result["tokens_in"], result["tokens_out"],
            current_state.get("rework", False),
            output=result["output"],
            run_name=run_name,
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

    col_name = _column_name(config, current_col, current_board)
    tokens_info = ""
    if result["tokens_in"] or result["tokens_out"]:
        tokens_info = f" | tokens: {result['tokens_in']}↑ {result['tokens_out']}↓"

    # commit + push + PR quando a coluna tem git_commit=true
    pr_url = None
    commit_ok = not _git_commit_flag(config, current_col, current_board)  # True se não precisa commitar
    if _git_commit_flag(config, current_col, current_board):
        branch = git.current_branch()
        flow = _flow_config(config, current_col, current_board)
        try:
            committed = git.commit(config, f"[#{current_state['issue_number']}] {role}: {current_state.get('current_feature', '')}")
            if not committed:
                logs.log_error(current_state["issue_number"], role, "agente não gravou arquivos — reexecutando na próxima rodada")
                current_state["last_error"] = "agente não produziu artefatos"
                current_state["status"] = "idle"
                current_state["rework"] = True
                state_mod.save(current_state)
                return
            commit_ok = True
            git.push(branch)
            logs.log_info(current_state["issue_number"], role, f"push concluído para branch '{branch}'")
            pr = github.open_pr(
                config,
                title=f"[#{current_state['issue_number']}] {current_state.get('current_feature', '')}",
                body=f"Gerado automaticamente após execução do agente `{role}`.\n\nFecha #{current_state['issue_number']}",
                head=branch,
                base=flow.get("merge", "main"),
            )
            pr_url = pr.get("url", "")
            logs.log_info(current_state["issue_number"], role, f"PR aberto: {pr_url}")
        except RuntimeError as e:
            logs.log_error(current_state["issue_number"], role, f"git commit/push/PR falhou: {e}")
            current_state["last_error"] = f"git commit/push/PR falhou: {e}"
            current_state["status"] = "idle"
            current_state["rework"] = True
            state_mod.save(current_state)
            return

    comment = f"✅ `{role}` concluído → `{col_name}` aguardando aprovação{tokens_info}"
    if pr_url:
        comment += f"\nPR: {pr_url}"
    github.post_comment(config, current_state["issue_number"], body=comment)
    github.move_card(config, current_state["issue_number"], col_name, _board_name_for_column(config, current_col, current_board))

    current_state["current_step"] = role
    current_state["current_column"] = current_col
    current_state["last_error"] = None
    current_state["status"] = "awaiting_approval"
    current_state["rework"] = False
    state_mod.save(current_state)


def _reset_state(state: dict) -> None:
    state.update(status="idle", current_step=None, current_column=None,
                 current_feature=None, issue_number=None, rework=False)


def _print_status(config: dict, sleep_s: float) -> None:
    from datetime import datetime
    state = state_mod.load()
    status = state.get("status", "idle")
    ts = datetime.now().strftime("%H:%M:%S")
    if status == "awaiting_approval":
        info = f"aguardando aprovação — #{state.get('issue_number')} / {state.get('current_step')}"
    elif state.get("current_feature"):
        info = f"processando #{state.get('issue_number')} — {state.get('current_feature')}"
    else:
        info = "aguardando issues"
    print(f"[{ts}] {info} (próximo ciclo em {int(sleep_s)}s)", flush=True)


def _finish_issue(config: dict, state: dict, sprint_issues: list[int], done_col_id: str, board_key: str | None = None) -> None:
    blocker.unblock_dependents(config, state["issue_number"])
    logs.log_issue_done(state["issue_number"])
    sprint_issues.append(state["issue_number"])
    github.move_card(config, state["issue_number"], _column_name(config, done_col_id, board_key), _board_name_for_column(config, done_col_id, board_key))
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
    print("Sincronizando boards...", flush=True)
    sync_boards(config)
    print("Boards sincronizados. Iniciando loop.", flush=True)
    sprint_issues: list[int] = []
    sprint_size = config.get("pipe", {}).get("sprint_size", 10)

    try:
        while True:
            run_once(config, sprint_issues)

            if len(sprint_issues) >= sprint_size:
                _run_optimizer(config, sprint_issues)
                sprint_issues = []

            sleep_s = (config.get("pipe", {}).get("sleeptime") or 1) * 60
            wait = poll_interval_s if poll_interval_s != 60 else sleep_s
            _print_status(config, wait)
            time.sleep(wait)
    except KeyboardInterrupt:
        print("\nInterrompido.", flush=True)
        if sprint_issues:
            _run_optimizer(config, sprint_issues)
