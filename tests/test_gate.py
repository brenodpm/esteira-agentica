import json
from unittest.mock import patch
import pytest

from src.orchestrator.runner import run_once
from src.orchestrator import state as state_mod

_CONFIG = {
    "repo": "org/repo",
    "metrics_db": ":memory:",
    "gitflow": {"branch_base": "develop"},
    "boards": {
        "task": {
            "todo": "backlog",
            "priority": 0,
            "columns": {
                "backlog": {
                    "name": "Backlog",
                    "change": {"advance": "dev", "cancelar": "cancelado"},
                },
                "dev": {
                    "name": "Dev",
                    "agent": "requirements",
                    "acao": "Implementar",
                    "change": {"advance": "review"},
                },
                "review": {
                    "name": "Review",
                    "agent": "architecture",
                    "change": {"advance": "concluido"},
                },
                "concluido": {"name": "Concluído"},
                "cancelado": {"name": "Cancelado"},
            },
        }
    },
}

_AWAITING = {
    "status": "awaiting_approval",
    "current_column": "dev",
    "current_step": "requirements",
    "current_feature": "feat",
    "issue_number": 1,
    "rework": False,
}

_IDLE_NEW = {
    "status": "idle",
    "current_column": None,
    "current_step": None,
    "current_feature": None,
    "issue_number": 1,
    "rework": False,
}

_AGENT_RESULT = {"output": "artefato gerado", "duration_s": 1.0, "tokens_in": None, "tokens_out": None}
_ISSUE = {"number": 1, "title": "feat", "body": "", "labels": [{"name": "dev"}]}


# CT-058 — pending: nenhuma ação, estado inalterado
def test_pending_no_action():
    with patch("src.orchestrator.runner.state_mod.load", return_value=dict(_AWAITING)), \
         patch("src.orchestrator.runner.github.issue_exists", return_value=True), \
         patch("src.orchestrator.runner.github.get_approval_status", return_value="pending"), \
         patch("src.orchestrator.runner.state_mod.save") as mock_save, \
         patch("src.orchestrator.runner.agents_run") as mock_agents:
        run_once(_CONFIG)
    mock_save.assert_not_called()
    mock_agents.assert_not_called()


# CT-059 — approved: avança para próxima coluna com agente, status volta a "idle"
def test_approved_advances_step():
    with patch("src.orchestrator.runner.state_mod.load", return_value=dict(_AWAITING)), \
         patch("src.orchestrator.runner.github.issue_exists", return_value=True), \
         patch("src.orchestrator.runner.github.get_approval_status", return_value="approved"), \
         patch("src.orchestrator.runner.github.remove_label") as mock_remove, \
         patch("src.orchestrator.runner.state_mod.save") as mock_save:
        run_once(_CONFIG)
    saved = mock_save.call_args[0][0]
    assert saved["status"] == "idle"
    assert saved["current_column"] == "review"
    assert saved["current_step"] == "architecture"
    mock_remove.assert_called_once_with(_CONFIG, 1, "approved")


# CT-060 — rejected: current_step mantido, rework=True
def test_rejected_sets_rework():
    with patch("src.orchestrator.runner.state_mod.load", return_value=dict(_AWAITING)), \
         patch("src.orchestrator.runner.github.issue_exists", return_value=True), \
         patch("src.orchestrator.runner.github.get_approval_status", return_value="rejected"), \
         patch("src.orchestrator.runner.github.remove_label") as mock_remove, \
         patch("src.orchestrator.runner.state_mod.save") as mock_save:
        run_once(_CONFIG)
    saved = mock_save.call_args[0][0]
    assert saved["current_step"] == "requirements"
    assert saved["rework"] is True
    mock_remove.assert_called_once_with(_CONFIG, 1, "rejected")


# CT-061 — re-execução com rework=True chama metrics.record com rework=True
def test_rework_metrics_record():
    rework_state = {**_IDLE_NEW, "current_column": "dev", "current_step": "requirements",
                    "current_feature": "feat", "rework": True}
    with patch("src.orchestrator.runner.state_mod.load", return_value=rework_state), \
         patch("src.orchestrator.runner.github.issue_exists", return_value=True), \
         patch("src.orchestrator.runner.github.get_issue", return_value=_ISSUE), \
         patch("src.orchestrator.runner.agents_run", return_value=_AGENT_RESULT), \
         patch("src.orchestrator.runner.metrics_record") as mock_metrics, \
         patch("src.orchestrator.runner.github.post_comment"), \
         patch("src.orchestrator.runner.github.move_card"), \
         patch("src.orchestrator.runner.state_mod.save"):
        run_once(_CONFIG)
    assert mock_metrics.call_args[1]["rework"] is True


# CT-062 — comentário pontual postado na issue após execução do agente (sem output completo)
def test_post_comment_after_agent():
    with patch("src.orchestrator.runner.state_mod.load", return_value=dict(_IDLE_NEW)), \
         patch("src.orchestrator.runner.github.issue_exists", return_value=True), \
         patch("src.orchestrator.runner.blocker.detect_deadlock", return_value=False), \
         patch("src.orchestrator.runner.priority.select_next", return_value=_ISSUE), \
         patch("src.orchestrator.runner.github.get_issue", return_value=_ISSUE), \
         patch("src.orchestrator.runner.git.create_branch"), \
         patch("src.orchestrator.runner.agents_run", return_value=_AGENT_RESULT), \
         patch("src.orchestrator.runner.metrics_record"), \
         patch("src.orchestrator.runner.github.post_comment") as mock_comment, \
         patch("src.orchestrator.runner.github.move_card"), \
         patch("src.orchestrator.runner.state_mod.save"):
        run_once(_CONFIG)
    body = mock_comment.call_args[1]["body"]
    assert "artefato gerado" not in body  # output completo não vai para a issue
    assert "requirements" in body          # agente mencionado
    assert "aguardando aprovação" in body  # status pontual


# CT-063 — estado salvo com status="awaiting_approval" após execução do agente
def test_state_awaiting_after_agent():
    with patch("src.orchestrator.runner.state_mod.load", return_value=dict(_IDLE_NEW)), \
         patch("src.orchestrator.runner.github.issue_exists", return_value=True), \
         patch("src.orchestrator.runner.blocker.detect_deadlock", return_value=False), \
         patch("src.orchestrator.runner.priority.select_next", return_value=_ISSUE), \
         patch("src.orchestrator.runner.github.get_issue", return_value=_ISSUE), \
         patch("src.orchestrator.runner.git.create_branch"), \
         patch("src.orchestrator.runner.agents_run", return_value=_AGENT_RESULT), \
         patch("src.orchestrator.runner.metrics_record"), \
         patch("src.orchestrator.runner.github.post_comment"), \
         patch("src.orchestrator.runner.github.move_card"), \
         patch("src.orchestrator.runner.state_mod.save") as mock_save:
        run_once(_CONFIG)
    saved = mock_save.call_args[0][0]
    assert saved["status"] == "awaiting_approval"
    assert saved["current_step"] == "requirements"


_CONFIG_GATE = {
    "repo": "org/repo",
    "metrics_db": ":memory:",
    "boards": {
        "demanda": {
            "todo": "backlog",
            "priority": 0,
            "flow": "doc",
            "columns": {
                "backlog": {"name": "Backlog", "change": {"advance": "analise"}},
                "analise": {
                    "name": "Análise",
                    "agent": "product",
                    "git_commit": True,
                    "acao": "Analisar",
                    "change": {"advance": "aprovacao"},
                },
                "aprovacao": {
                    "name": "Aprovação",
                    "git_merge": True,
                    "change": {"advance": "criacao"},
                },
                "criacao": {
                    "name": "Criação",
                    "agent": "product",
                    "git_commit": True,
                    "acao": "Criar",
                    "change": {"advance": "concluido"},
                },
                "concluido": {"name": "Concluído"},
            },
        }
    },
}

_AWAITING_ANALISE = {
    "status": "awaiting_approval",
    "current_column": "analise",
    "current_step": "product",
    "current_feature": "feat",
    "issue_number": 1,
    "rework": False,
}

_AWAITING_APROVACAO = {
    "status": "awaiting_approval",
    "current_column": "aprovacao",
    "current_step": None,
    "current_feature": "feat",
    "issue_number": 1,
    "rework": False,
}


# CT-065 — aprovação em coluna com agente → próxima é gate humano (sem agente): move card e awaiting_approval
def test_approved_moves_to_human_gate():
    with patch("src.orchestrator.runner.state_mod.load", return_value=dict(_AWAITING_ANALISE)), \
         patch("src.orchestrator.runner.github.issue_exists", return_value=True), \
         patch("src.orchestrator.runner.github.get_approval_status", return_value="approved"), \
         patch("src.orchestrator.runner.github.remove_label"), \
         patch("src.orchestrator.runner.github.move_card") as mock_move, \
         patch("src.orchestrator.runner.state_mod.save") as mock_save:
        run_once(_CONFIG_GATE)
    saved = mock_save.call_args[0][0]
    assert saved["status"] == "awaiting_approval"
    assert saved["current_column"] == "aprovacao"
    assert saved["current_step"] is None
    mock_move.assert_called_once_with(_CONFIG_GATE, 1, "Aprovação", None)


# CT-066 — aprovação no gate humano → avança para coluna com agente, status=idle
def test_approved_from_human_gate_advances():
    with patch("src.orchestrator.runner.state_mod.load", return_value=dict(_AWAITING_APROVACAO)), \
         patch("src.orchestrator.runner.github.issue_exists", return_value=True), \
         patch("src.orchestrator.runner.github.get_approval_status", return_value="approved"), \
         patch("src.orchestrator.runner.github.remove_label"), \
         patch("src.orchestrator.runner.github.move_card"), \
         patch("src.orchestrator.runner.state_mod.save") as mock_save:
        run_once(_CONFIG_GATE)
    saved = mock_save.call_args[0][0]
    assert saved["status"] == "idle"
    assert saved["current_column"] == "criacao"
    assert saved["current_step"] == "product"


# CT-064 — estado "awaiting_approval" persiste após reinicialização
def test_awaiting_approval_persists(tmp_path):
    data = {"status": "awaiting_approval", "current_column": "dev", "current_step": "requirements",
            "issue_number": 1, "rework": False}
    p = tmp_path / "state.json"
    p.write_text(json.dumps(data))
    result = state_mod.load(p)
    assert result["status"] == "awaiting_approval"
    assert result["current_step"] == "requirements"
    assert result["rework"] is False
