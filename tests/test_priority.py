from unittest.mock import patch
import pytest

from src.orchestrator.priority import select_next, get_current_milestone
from src.orchestrator.runner import run_once

_CONFIG = {
    "repo": "org/repo",
    "agents_sequence": ["requirements", "architecture"],
    "metrics_db": ":memory:",
    "board": {"columns": ["Backlog", "In Progress", "Done"], "labels": {}},
    "gitflow": {"branch_base": "develop", "prefixes": {"feature": "feature/"}},
}

_STATE_M1 = {"current_milestone": "m1"}
_STATE_EMPTY = {}

# Helpers
def _issue(number, labels=None, created_at="2026-01-01", body=""):
    return {
        "number": number,
        "title": f"issue {number}",
        "labels": [{"name": l} for l in (labels or [])],
        "createdAt": created_at,
        "body": body,
    }

def _sub(number, labels=None, created_at="2026-01-01", parent=1):
    """Sub-issue: body references parent via #N."""
    return _issue(number, labels, created_at, body=f"Depends on #{parent}")


# CT-075 — sub-issue in-progress > sub-issue backlog
def test_inprogress_sub_beats_backlog_sub():
    issues = [
        _sub(10, ["in-progress"], "2026-01-02"),
        _sub(11, [], "2026-01-01"),
    ]
    with patch("src.orchestrator.priority.github.get_issues", return_value=issues), \
         patch("src.orchestrator.priority.github.get_milestones", return_value=["m1"]):
        result = select_next(_CONFIG, _STATE_M1)
    assert result["number"] == 10


# CT-076 — sub-issue in-progress > top-level milestone issue
def test_inprogress_sub_beats_toplevel():
    issues = [
        _sub(10, ["in-progress"]),
        _issue(20, []),
    ]
    with patch("src.orchestrator.priority.github.get_issues", return_value=issues), \
         patch("src.orchestrator.priority.github.get_milestones", return_value=["m1"]):
        result = select_next(_CONFIG, _STATE_M1)
    assert result["number"] == 10


# CT-077 — sub-issue backlog > top-level milestone issue
def test_backlog_sub_beats_toplevel():
    issues = [
        _sub(11, [], "2026-01-02"),
        _issue(20, [], "2026-01-01"),
    ]
    with patch("src.orchestrator.priority.github.get_issues", return_value=issues), \
         patch("src.orchestrator.priority.github.get_milestones", return_value=["m1"]):
        result = select_next(_CONFIG, _STATE_M1)
    assert result["number"] == 11


# CT-078 — milestone corrente > milestone futuro
def test_current_milestone_beats_future():
    m1_issues = [_issue(20, [])]
    m2_issues = [_issue(30, [])]
    def mock_get_issues(config, milestone):
        return m1_issues if milestone == "m1" else m2_issues
    with patch("src.orchestrator.priority.github.get_issues", side_effect=mock_get_issues), \
         patch("src.orchestrator.priority.github.get_milestones", return_value=["m1", "m2"]):
        result = select_next(_CONFIG, _STATE_M1)
    assert result["number"] == 20


# CT-079 — novo milestone só iniciado quando corrente está vazio
def test_next_milestone_when_current_empty():
    def mock_get_issues(config, milestone):
        return [] if milestone == "m1" else [_issue(30, [])]
    with patch("src.orchestrator.priority.github.get_issues", side_effect=mock_get_issues), \
         patch("src.orchestrator.priority.github.get_milestones", return_value=["m1", "m2"]):
        result = select_next(_CONFIG, _STATE_M1)
    assert result["number"] == 30


# CT-080 — issues com blocked ignoradas em todos os níveis
def test_blocked_ignored_all_levels():
    issues = [
        _sub(10, ["in-progress", "blocked"]),
        _sub(11, ["blocked"]),
        _issue(20, ["blocked"]),
    ]
    with patch("src.orchestrator.priority.github.get_issues", return_value=issues), \
         patch("src.orchestrator.priority.github.get_milestones", return_value=["m1"]):
        result = select_next(_CONFIG, _STATE_M1)
    assert result is None


# CT-081 — issues com needs-human ignoradas
def test_needs_human_ignored():
    issues = [_issue(10, ["needs-human"])]
    with patch("src.orchestrator.priority.github.get_issues", return_value=issues), \
         patch("src.orchestrator.priority.github.get_milestones", return_value=["m1"]):
        result = select_next(_CONFIG, _STATE_M1)
    assert result is None


# CT-082 — empate: retorna a mais antiga
def test_tiebreak_oldest_first():
    issues = [
        _sub(11, [], "2026-01-03"),
        _sub(12, [], "2026-01-01"),
    ]
    with patch("src.orchestrator.priority.github.get_issues", return_value=issues), \
         patch("src.orchestrator.priority.github.get_milestones", return_value=["m1"]):
        result = select_next(_CONFIG, _STATE_M1)
    assert result["number"] == 12


# CT-083 — retorna None quando não há nenhuma issue disponível
def test_returns_none_when_no_issues():
    with patch("src.orchestrator.priority.github.get_issues", return_value=[]), \
         patch("src.orchestrator.priority.github.get_milestones", return_value=["m1"]):
        result = select_next(_CONFIG, _STATE_M1)
    assert result is None


# CT-084 — get_current_milestone retorna milestone do estado
def test_get_current_milestone_from_state():
    result = get_current_milestone(_CONFIG, {"current_milestone": "m2"})
    assert result == "m2"


# CT-085 — get_current_milestone retorna primeiro milestone com issues abertas
def test_get_current_milestone_from_github():
    def mock_get_issues(config, milestone):
        return [_issue(1)] if milestone == "m1" else []
    with patch("src.orchestrator.priority.github.get_milestones", return_value=["m1", "m2"]), \
         patch("src.orchestrator.priority.github.get_issues", side_effect=mock_get_issues):
        result = get_current_milestone(_CONFIG, {})
    assert result == "m1"


# CT-086 — run_once usa priority.select_next em vez de github.get_next_issue
def test_run_once_uses_priority_select_next():
    idle_state = {"status": "idle", "current_step": None, "current_feature": None, "issue_number": None, "rework": False}
    with patch("src.orchestrator.runner.state_mod.load", return_value=idle_state), \
         patch("src.orchestrator.runner.blocker.detect_deadlock", return_value=False), \
         patch("src.orchestrator.runner.priority.select_next", return_value=None) as mock_select, \
         patch("src.orchestrator.runner.github.get_next_issue") as mock_get_next, \
         patch("src.orchestrator.runner.agents_run"):
        run_once(_CONFIG)
    mock_select.assert_called_once()
    mock_get_next.assert_not_called()
