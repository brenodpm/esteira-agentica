import json
import os
from unittest.mock import patch, MagicMock, call
import pytest

from src.orchestrator import state as state_mod
from src.orchestrator.runner import run_once, run_loop

_CONFIG = {
    "repo": "org/repo",
    "agents_sequence": ["requirements", "architecture"],
    "metrics_db": ":memory:",
    "board": {"columns": ["Backlog", "In Progress", "Done"], "labels": {}},
    "gitflow": {"branch_base": "develop", "prefixes": {"feature": "feature/"}},
}

_IDLE_STATE = {"current_feature": None, "current_step": None, "status": "idle", "issue_number": None}
_ISSUE = {"number": 1, "title": "feat: nova feature"}
_AGENT_RESULT = {"output": "ok", "duration_s": 1.0, "tokens_in": None, "tokens_out": None}


# CT-049 — state.load retorna estado inicial quando arquivo não existe
def test_state_load_missing_file(tmp_path):
    result = state_mod.load(tmp_path / "nao_existe.json")
    assert result == {"current_feature": None, "current_step": None, "status": "idle", "issue_number": None, "rework": False}


# CT-050 — state.load retorna conteúdo do arquivo quando existe
def test_state_load_existing_file(tmp_path):
    data = {"current_feature": "f1", "current_step": "requirements", "status": "running", "issue_number": 42}
    p = tmp_path / "state.json"
    p.write_text(json.dumps(data))
    assert state_mod.load(p) == data


# CT-051 — state.save usa escrita atômica (arquivo temporário + os.replace)
def test_state_save_atomic(tmp_path):
    p = tmp_path / "state.json"
    with patch("os.replace", wraps=os.replace) as mock_replace:
        state_mod.save({"status": "idle"}, p)
    mock_replace.assert_called_once()
    tmp_arg, final_arg = mock_replace.call_args[0]
    assert str(tmp_arg) != str(final_arg)
    assert str(final_arg) == str(p)
    assert json.loads(p.read_text()) == {"status": "idle"}


# CT-052 — run_once retorna sem erro e sem alterar estado quando backlog vazio
def test_run_once_empty_backlog():
    with patch("src.orchestrator.runner.state_mod.load", return_value=dict(_IDLE_STATE)), \
         patch("src.orchestrator.runner.blocker.detect_deadlock", return_value=False), \
         patch("src.orchestrator.runner.github.get_next_issue", return_value=None), \
         patch("src.orchestrator.runner.state_mod.save") as mock_save, \
         patch("src.orchestrator.runner.agents_run") as mock_agents:
        run_once(_CONFIG)
    mock_save.assert_not_called()
    mock_agents.assert_not_called()


# CT-053 — run_once avança current_step após execução bem-sucedida do agente
def test_run_once_advances_step():
    with patch("src.orchestrator.runner.state_mod.load", return_value=dict(_IDLE_STATE)), \
         patch("src.orchestrator.runner.github.get_next_issue", return_value=_ISSUE), \
         patch("src.orchestrator.runner.git.create_branch"), \
         patch("src.orchestrator.runner.agents_run", return_value=_AGENT_RESULT), \
         patch("src.orchestrator.runner.metrics_record"), \
         patch("src.orchestrator.runner.github.post_comment"), \
         patch("src.orchestrator.runner.github.move_card"), \
         patch("src.orchestrator.runner.state_mod.save") as mock_save:
        run_once(_CONFIG)
    saved_state = mock_save.call_args[0][0]
    assert saved_state["current_step"] == "requirements"


# CT-054 — run_once cria branch apenas no início de uma nova feature
def test_run_once_creates_branch_on_new_feature():
    with patch("src.orchestrator.runner.state_mod.load", return_value=dict(_IDLE_STATE)), \
         patch("src.orchestrator.runner.github.get_next_issue", return_value=_ISSUE), \
         patch("src.orchestrator.runner.git.create_branch") as mock_branch, \
         patch("src.orchestrator.runner.agents_run", return_value=_AGENT_RESULT), \
         patch("src.orchestrator.runner.metrics_record"), \
         patch("src.orchestrator.runner.github.post_comment"), \
         patch("src.orchestrator.runner.github.move_card"), \
         patch("src.orchestrator.runner.state_mod.save"):
        run_once(_CONFIG)
    mock_branch.assert_called_once()


# CT-055 — run_once não cria branch quando current_step já está definido
def test_run_once_no_branch_on_resume():
    resume_state = {"current_feature": "feat", "current_step": "requirements", "status": "running", "issue_number": 1}
    with patch("src.orchestrator.runner.state_mod.load", return_value=resume_state), \
         patch("src.orchestrator.runner.github.get_next_issue", return_value=_ISSUE), \
         patch("src.orchestrator.runner.git.create_branch") as mock_branch, \
         patch("src.orchestrator.runner.agents_run", return_value=_AGENT_RESULT), \
         patch("src.orchestrator.runner.metrics_record"), \
         patch("src.orchestrator.runner.github.post_comment"), \
         patch("src.orchestrator.runner.github.move_card"), \
         patch("src.orchestrator.runner.state_mod.save"):
        run_once(_CONFIG)
    mock_branch.assert_not_called()


# CT-056 — run_loop encerra sem stack trace ao receber KeyboardInterrupt
def test_run_loop_keyboard_interrupt():
    with patch("src.orchestrator.runner.run_once", side_effect=KeyboardInterrupt), \
         patch("src.orchestrator.runner.time.sleep"):
        run_loop(_CONFIG, poll_interval_s=0)  # must not raise


# CT-057 — run_once registra execução em metrics.record após agente concluir
def test_run_once_records_metrics():
    agent_result = {"output": "ok", "duration_s": 2.5, "tokens_in": 10, "tokens_out": 20}
    with patch("src.orchestrator.runner.state_mod.load", return_value=dict(_IDLE_STATE)), \
         patch("src.orchestrator.runner.github.get_next_issue", return_value=_ISSUE), \
         patch("src.orchestrator.runner.git.create_branch"), \
         patch("src.orchestrator.runner.agents_run", return_value=agent_result), \
         patch("src.orchestrator.runner.metrics_record") as mock_metrics, \
         patch("src.orchestrator.runner.github.post_comment"), \
         patch("src.orchestrator.runner.github.move_card"), \
         patch("src.orchestrator.runner.state_mod.save"):
        run_once(_CONFIG)
    kwargs = mock_metrics.call_args[1]
    assert kwargs["duration_s"] == 2.5
    assert kwargs["tokens_in"] == 10
    assert kwargs["tokens_out"] == 20
