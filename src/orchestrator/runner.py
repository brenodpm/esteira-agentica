import time

from src.orchestrator import state as state_mod
from src.integrations import github, git
from src.agents import run as agents_run
from src.metrics import record as metrics_record


def run_once(config: dict) -> None:
    current_state = state_mod.load()

    if current_state["status"] == "idle":
        issue = github.get_next_issue(config)
        if issue is None:
            return
        current_state["issue_number"] = issue["number"]
        current_state["current_feature"] = issue["title"]
        current_state["status"] = "running"

    sequence = config["agents_sequence"]
    current_step = current_state["current_step"]

    if current_step is None:
        git.create_branch(config, current_state["current_feature"])
        step_index = 0
    else:
        step_index = sequence.index(current_step) + 1

    if step_index >= len(sequence):
        current_state["status"] = "idle"
        current_state["current_step"] = None
        current_state["current_feature"] = None
        current_state["issue_number"] = None
        state_mod.save(current_state)
        return

    role = sequence[step_index]
    result = agents_run(role=role, context_files=[], prompt=current_state["current_feature"] or "")

    metrics_record(
        path=config.get("metrics_db", "metrics.db"),
        feature_id=str(current_state["issue_number"]),
        agent=role,
        duration_s=result["duration_s"],
        tokens_in=result["tokens_in"],
        tokens_out=result["tokens_out"],
    )

    current_state["current_step"] = role
    state_mod.save(current_state)
    github.move_card(config, current_state["issue_number"], "In Progress")


def run_loop(config: dict, poll_interval_s: int = 60) -> None:
    try:
        while True:
            run_once(config)
            time.sleep(poll_interval_s)
    except KeyboardInterrupt:
        pass
