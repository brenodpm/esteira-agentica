import json
import subprocess
from unittest.mock import patch, MagicMock

import pytest

from src.integrations.github import (
    get_next_issue,
    get_issue,
    post_comment,
    add_label,
    remove_label,
    move_card,
    open_pr,
    create_issue,
    get_approval_status,
)

CONFIG = {"repo": "org/repo"}


def _mock_run(stdout: str):
    m = MagicMock()
    m.stdout = stdout
    return m


def _issue(number: int, labels: list[str], created_at: str = "2024-01-01T00:00:00Z") -> dict:
    return {
        "number": number,
        "title": f"Issue {number}",
        "labels": [{"name": l} for l in labels],
        "createdAt": created_at,
    }


# CT-016
def test_get_next_issue_returns_none_when_backlog_empty():
    with patch("subprocess.run", return_value=_mock_run("[]")):
        assert get_next_issue(CONFIG) is None


# CT-017
def test_get_next_issue_skips_blocked():
    issues = [_issue(1, ["blocked"])]
    with patch("subprocess.run", return_value=_mock_run(json.dumps(issues))):
        assert get_next_issue(CONFIG) is None


# CT-018
def test_get_next_issue_skips_needs_human():
    issues = [_issue(1, ["needs-human"])]
    with patch("subprocess.run", return_value=_mock_run(json.dumps(issues))):
        assert get_next_issue(CONFIG) is None


# CT-019
def test_get_next_issue_returns_oldest_eligible():
    issues = [
        _issue(2, [], "2024-02-01T00:00:00Z"),
        _issue(1, [], "2024-01-01T00:00:00Z"),
    ]
    with patch("subprocess.run", return_value=_mock_run(json.dumps(issues))):
        result = get_next_issue(CONFIG)
    assert result["number"] == 1


# CT-020
def test_get_approval_status_approved():
    issue = _issue(1, ["approved"])
    with patch("subprocess.run", return_value=_mock_run(json.dumps(issue))):
        assert get_approval_status(CONFIG, 1) == "approved"


# CT-021
def test_get_approval_status_rejected():
    issue = _issue(1, ["rejected"])
    with patch("subprocess.run", return_value=_mock_run(json.dumps(issue))):
        assert get_approval_status(CONFIG, 1) == "rejected"


# CT-022
def test_get_approval_status_pending():
    issue = _issue(1, ["in-progress"])
    with patch("subprocess.run", return_value=_mock_run(json.dumps(issue))):
        assert get_approval_status(CONFIG, 1) == "pending"


# CT-023
def test_gh_error_propagates_as_runtime_error():
    err = subprocess.CalledProcessError(1, "gh", stderr="not found")
    with patch("subprocess.run", side_effect=err):
        with pytest.raises(RuntimeError, match="not found"):
            get_issue(CONFIG, 1)


# CT-024
def test_all_public_symbols_are_callable():
    for fn in [get_next_issue, get_issue, post_comment, add_label, remove_label,
               move_card, open_pr, create_issue, get_approval_status]:
        assert callable(fn)


# CT-025
def test_get_next_issue_returns_eligible_among_blocked():
    issues = [
        _issue(1, ["blocked"], "2024-01-01T00:00:00Z"),
        _issue(2, [], "2024-01-02T00:00:00Z"),
    ]
    with patch("subprocess.run", return_value=_mock_run(json.dumps(issues))):
        result = get_next_issue(CONFIG)
    assert result["number"] == 2
