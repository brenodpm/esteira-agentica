"""Testes de conflito e rate limit."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.github import RateLimitError


@pytest.fixture(autouse=True)
def setup_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr("src.issues.BOARDS_DIR", tmp_path / ".pipe" / "boards")
    monkeypatch.setattr("src.issues.PIPE_DIR", tmp_path / ".pipe")
    monkeypatch.setattr("src.issues.SNAPSHOT_FILE", tmp_path / ".pipe" / "snapshot.json")
    (tmp_path / ".pipe").mkdir()
    (tmp_path / ".pipe" / "boards" / "task" / "backlog").mkdir(parents=True)
    (tmp_path / ".pipe" / "boards" / "task" / "dev").mkdir(parents=True)


def _config():
    return {
        "repo": "owner/repo",
        "boards": {
            "task": {
                "columns": {
                    "backlog": {"name": "Backlog"},
                    "dev": {"name": "Desenvolvimento"},
                }
            }
        },
        "boards_meta": {"create-remote-boards": False, "allow-del-remote-issue": False},
    }


def _write_snapshot(tmp_path, data):
    (tmp_path / ".pipe" / "snapshot.json").write_text(json.dumps(data))


class TestConflito:
    """Movimentação simultânea local+remota: local vence (etapa 2 antes da 3)."""

    @patch("src.issues.fetch_updated_issues", return_value=[42])
    @patch("src.issues.fetch_board_items_graphql", return_value=[
        {"item_id": "PVTI_1", "number": 42, "title": "Issue", "url": "", "body": "Body", "status": "Backlog", "updated_at": "2026-06-15T12:00:00Z"}
    ])
    @patch("src.issues.resolve_project_metadata", return_value={"project_id": "P1", "status_field_id": "F1", "options": {}, "items": {}})
    @patch("src.issues.fetch_issue_comments", return_value={"updatedAt": "2026-06-15T12:00:00Z", "comments": []})
    @patch("src.issues.move_card")
    @patch("src.issues.update_issue_body")
    @patch("src.issues._build_history", return_value=("", "2026-06-15T12:00:00Z"))
    def test_local_vence_conflito(self, mock_hist, mock_body, mock_move,
                                  mock_comments, mock_meta, mock_items_gql,
                                  mock_updated, tmp_path):
        """Se issue foi movida localmente (l-sync) e remotamente, local vence."""
        from src.issues import sync_issues

        # Issue movida localmente para dev
        dev_dir = tmp_path / ".pipe" / "boards" / "task" / "dev"
        issue_file = dev_dir / "42-issue.md"
        issue_file.write_text("# Issue\n\nBody\n")

        _write_snapshot(tmp_path, {
            "issues": {"task": [{
                "id": 42, "name": "Issue", "column": "backlog",
                "path": str(tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue.md"),
                "history_path": str(tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue-history.md"),
                "write_path": str(tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue-write.md"),
                "l-time": "0", "b-time": "2026-06-15T10:00:00Z", "status": "ok",
            }]},
            "cache": {},
            "last_sync": "2026-06-15T10:00:00Z",
        })

        sync_issues(_config())

        # Local vence: move_card chamado (propaga local → GitHub)
        mock_move.assert_called_once()
        # Etapa 3 não deve mover de volta porque status já não é "ok"
        # (foi setado para "ok" pela etapa 2)


class TestRateLimit:
    """Verifica que rate limit é tratado graciosamente."""

    @patch("src.issues.move_card", side_effect=RateLimitError("rate limit"))
    @patch("src.issues.update_issue_body")
    @patch("src.issues._build_history", return_value=("", ""))
    def test_rate_limit_para_etapa2(self, mock_hist, mock_body, mock_move, tmp_path):
        """Rate limit durante etapa 2 propaga RateLimitError e preserva status."""
        from src.issues import _etapa2_snapshot_para_github
        import pytest

        board_dir = tmp_path / ".pipe" / "boards" / "task" / "dev"
        issue_file = board_dir / "42-issue.md"
        issue_file.write_text("# Issue\n\nBody\n")
        write_file = board_dir / "42-issue-write.md"
        write_file.write_text("")

        snapshot = {"issues": {"task": [{
            "id": 42, "name": "Issue", "column": "dev",
            "path": str(issue_file),
            "history_path": str(board_dir / "42-issue-history.md"),
            "write_path": str(write_file),
            "l-time": "999", "b-time": "2025-01-01T00:00:00Z", "status": "l-sync",
        }]}, "cache": {}}

        # Deve propagar RateLimitError para o main loop tratar
        with pytest.raises(RateLimitError):
            _etapa2_snapshot_para_github(snapshot, _config())

        # Issue permanece l-sync para retry no próximo ciclo
        assert snapshot["issues"]["task"][0]["status"] == "l-sync"

    @patch("src.issues.fetch_updated_issues", side_effect=RateLimitError("rate limit"))
    def test_rate_limit_etapa3_graceful(self, mock_updated, tmp_path):
        """Rate limit na etapa 3 não crasha, retorna 0."""
        from src.issues import _etapa3_github_para_snapshot

        snapshot = {
            "issues": {"task": []},
            "cache": {},
            "last_sync": "2026-06-15T10:00:00Z",
        }

        count = _etapa3_github_para_snapshot(snapshot, _config())
        assert count == 0


class TestShouldFullSync:
    """Testa lógica de virada de dia."""

    def test_sem_last_sync(self):
        from src.sync import should_full_sync
        assert should_full_sync({}) is True

    def test_mesmo_dia(self):
        from src.sync import should_full_sync
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        assert should_full_sync({"last_sync": now}) is False

    def test_dia_anterior(self):
        from src.sync import should_full_sync
        assert should_full_sync({"last_sync": "2020-01-01T00:00:00Z"}) is True
