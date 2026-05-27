from unittest.mock import patch, call
import pytest

from src.orchestrator.blocker import create_blocker, unblock_dependents, detect_deadlock
from src.orchestrator.runner import run_once

_CONFIG = {
    "repo": "org/repo",
    "agents_sequence": ["requirements", "architecture"],
    "metrics_db": ":memory:",
    "board": {"columns": ["Backlog", "In Progress", "Done"], "labels": {}},
    "gitflow": {"branch_base": "develop", "prefixes": {"feature": "feature/"}},
}

_IDLE_STATE = {"status": "idle", "current_step": None, "current_feature": None, "issue_number": None, "rework": False}
_AGENT_RESULT = {"output": "ok", "duration_s": 1.0, "tokens_in": None, "tokens_out": None}
_ISSUE = {"number": 1, "title": "feat"}


# CT-065 — create_blocker cria issue e adiciona label blocked na issue corrente
def test_create_blocker_basic():
    with patch("src.orchestrator.blocker.github.create_issue", return_value={"number": 42}) as mock_create, \
         patch("src.orchestrator.blocker.github.add_label") as mock_label:
        result = create_blocker(_CONFIG, blocked_issue=10, title="Depende de X", body="Descrição do bloqueio")
    mock_create.assert_called_once_with(_CONFIG, title="Depende de X", body="Descrição do bloqueio", labels=[])
    mock_label.assert_any_call(_CONFIG, 10, "blocked")
    assert result == 42


# CT-066 — create_blocker com needs_human=True adiciona label needs-human na issue criada
def test_create_blocker_needs_human():
    with patch("src.orchestrator.blocker.github.create_issue", return_value={"number": 43}), \
         patch("src.orchestrator.blocker.github.add_label") as mock_label:
        create_blocker(_CONFIG, blocked_issue=11, title="Pergunta ao humano", body="...", needs_human=True)
    calls = mock_label.call_args_list
    assert call(_CONFIG, 43, "needs-human") in calls
    assert call(_CONFIG, 11, "blocked") in calls


# CT-067 — create_blocker com needs_human=False não adiciona label needs-human
def test_create_blocker_no_needs_human():
    with patch("src.orchestrator.blocker.github.create_issue", return_value={"number": 44}), \
         patch("src.orchestrator.blocker.github.add_label") as mock_label:
        create_blocker(_CONFIG, blocked_issue=12, title="Bloqueio técnico", body="...", needs_human=False)
    labels_added = [c.args[2] for c in mock_label.call_args_list]
    assert "needs-human" not in labels_added


# CT-068 — unblock_dependents remove label blocked de issues que referenciam a issue resolvida
def test_unblock_dependents_removes_blocked():
    blocked_issues = [
        {"number": 20, "body": "Depende de #5 para continuar"},
        {"number": 21, "body": "Bloqueado por #5"},
    ]
    with patch("src.orchestrator.blocker.github.get_issues_with_label", return_value=blocked_issues), \
         patch("src.orchestrator.blocker.github.remove_label") as mock_remove, \
         patch("src.orchestrator.blocker.github.move_card") as mock_move:
        result = unblock_dependents(_CONFIG, resolved_issue=5)
    mock_remove.assert_any_call(_CONFIG, 20, "blocked")
    mock_remove.assert_any_call(_CONFIG, 21, "blocked")
    mock_move.assert_any_call(_CONFIG, 20, "Backlog")
    mock_move.assert_any_call(_CONFIG, 21, "Backlog")
    assert result == [20, 21]


# CT-069 — unblock_dependents retorna lista vazia quando nenhuma issue referencia a issue resolvida
def test_unblock_dependents_empty():
    with patch("src.orchestrator.blocker.github.get_issues_with_label", return_value=[]), \
         patch("src.orchestrator.blocker.github.remove_label") as mock_remove:
        result = unblock_dependents(_CONFIG, resolved_issue=99)
    mock_remove.assert_not_called()
    assert result == []


# CT-070 — detect_deadlock retorna True quando todas as issues disponíveis têm label blocked
def test_detect_deadlock_true():
    with patch("src.orchestrator.blocker.github.get_next_issue", return_value=None), \
         patch("src.orchestrator.blocker.github.get_issues_with_label", return_value=[{"number": 30}, {"number": 31}]):
        assert detect_deadlock(_CONFIG) is True


# CT-071 — detect_deadlock retorna False quando há pelo menos uma issue sem label blocked
def test_detect_deadlock_false():
    with patch("src.orchestrator.blocker.github.get_next_issue", return_value={"number": 32, "title": "feat"}):
        assert detect_deadlock(_CONFIG) is False


# CT-072 — run_once exclui issues com label blocked ao selecionar próxima issue
def test_run_once_skips_blocked():
    with patch("src.orchestrator.runner.state_mod.load", return_value=dict(_IDLE_STATE)), \
         patch("src.orchestrator.runner.blocker.detect_deadlock", return_value=False), \
         patch("src.orchestrator.runner.priority.select_next", return_value=None) as mock_next, \
         patch("src.orchestrator.runner.state_mod.save") as mock_save, \
         patch("src.orchestrator.runner.agents_run") as mock_agents:
        run_once(_CONFIG)
    mock_next.assert_called_once()
    mock_agents.assert_not_called()


# CT-073 — run_once chama unblock_dependents após conclusão de issue (last step approved)
def test_run_once_unblocks_on_completion():
    # Simulate last step approved: current_step is last in sequence
    awaiting_state = {
        "status": "awaiting_approval",
        "current_step": "architecture",  # last step
        "current_feature": "feat",
        "issue_number": 5,
        "rework": False,
    }
    with patch("src.orchestrator.runner.state_mod.load", return_value=awaiting_state), \
         patch("src.orchestrator.runner.github.get_approval_status", return_value="approved"), \
         patch("src.orchestrator.runner.github.remove_label"), \
         patch("src.orchestrator.runner.blocker.unblock_dependents") as mock_unblock, \
         patch("src.orchestrator.runner.state_mod.save"):
        run_once(_CONFIG)
    mock_unblock.assert_called_once_with(_CONFIG, 5)


# CT-074 — Deadlock detectado cria issue needs-human e para o loop
def test_run_once_deadlock_creates_issue():
    with patch("src.orchestrator.runner.state_mod.load", return_value=dict(_IDLE_STATE)), \
         patch("src.orchestrator.runner.blocker.detect_deadlock", return_value=True), \
         patch("src.orchestrator.runner.github.create_issue") as mock_create, \
         patch("src.orchestrator.runner.agents_run") as mock_agents:
        run_once(_CONFIG)
    mock_create.assert_called_once()
    _, kwargs = mock_create.call_args
    assert "needs-human" in kwargs.get("labels", [])
    mock_agents.assert_not_called()
