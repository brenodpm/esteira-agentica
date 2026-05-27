import time

from src.orchestrator import state as state_mod
from src.integrations import github, git
from src.agents import run as agents_run
from src.metrics import record as metrics_record


def run_once(config: dict) -> None:
    current_state = state_mod.load()
    status = current_state["status"]

    # --- Gate: awaiting human approval ---
    if status == "awaiting_approval":
        approval = github.get_approval_status(config, current_state["issue_number"])
        if approval == "pending":
            return
        if approval == "approved":
            github.remove_label(config, current_state["issue_number"], "approved")
            sequence = config["agents_sequence"]
            step_index = sequence.index(current_state["current_step"]) + 1
            if step_index >= len(sequence):
                current_state.update(status="idle", current_step=None, current_feature=None, issue_number=None, rework=False)
            else:
                current_state["current_step"] = sequence[step_index]
                current_state["status"] = "idle"
                current_state["rework"] = False
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
        if current_state.get("current_feature") is None:
            issue = github.get_next_issue(config)
            if issue is None:
                return
            current_state["issue_number"] = issue["number"]
            current_state["current_feature"] = issue["title"]

    sequence = config["agents_sequence"]
    current_step = current_state["current_step"]

    if current_step is None:
        git.create_branch(config, current_state["current_feature"])
        role = sequence[0]
    else:
        role = current_step  # rework: re-run same step; or already set by approval advance

    result = agents_run(role=role, context_files=[], prompt=current_state["current_feature"] or "")

    metrics_record(
        path=config.get("metrics_db", "metrics.db"),
        feature_id=str(current_state["issue_number"]),
        agent=role,
        duration_s=result["duration_s"],
        tokens_in=result["tokens_in"],
        tokens_out=result["tokens_out"],
        rework=current_state.get("rework", False),
    )

    github.post_comment(config, current_state["issue_number"], body=result["output"])

    current_state["current_step"] = role
    current_state["status"] = "awaiting_approval"
    current_state["rework"] = False
    state_mod.save(current_state)
    github.move_card(config, current_state["issue_number"], "In Progress")


def run_loop(config: dict, poll_interval_s: int = 60) -> None:
    try:
        while True:
            run_once(config)
            time.sleep(poll_interval_s)
    except KeyboardInterrupt:
        pass
