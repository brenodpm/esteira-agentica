"""Testes de integração: ciclo completo de sync_issues com mock do gh CLI."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


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


class TestCicloCompleto:
    """Simula ciclo completo: detecta l-new, cria no GitHub, resolve."""

    @patch("src.issues.fetch_updated_issues", return_value=[])
    @patch("src.issues.fetch_board_items_graphql", return_value=[])
    @patch("src.issues.resolve_project_metadata", return_value={"project_id": "P1", "status_field_id": "F1", "options": {}, "items": {}})
    @patch("src.issues.move_card")
    @patch("src.issues.add_issue_to_project", return_value="PVTI_123")
    @patch("src.issues.get_issue_node_id", return_value="I_node1")
    @patch("src.issues.create_issue", return_value=100)
    def test_l_new_ciclo(self, mock_create, mock_node, mock_add, mock_move,
                         mock_meta, mock_items_gql, mock_updated, tmp_path):
        from src.issues import sync_issues

        # Criar arquivo local novo
        board_dir = tmp_path / ".pipe" / "boards" / "task" / "backlog"
        (board_dir / "0-nova_tarefa.md").write_text("# Nova Tarefa\n\nDescrição\n")

        # Snapshot existente sem essa issue
        _write_snapshot(tmp_path, {
            "issues": {"task": []},
            "cache": {},
            "last_sync": "2026-06-15T10:00:00Z",
        })

        result = sync_issues(_config())

        assert result is True
        mock_create.assert_called_once()

    @patch("src.issues.fetch_updated_issues", return_value=[])
    @patch("src.issues.fetch_board_items_graphql", return_value=[])
    @patch("src.issues.resolve_project_metadata", return_value={"project_id": "P1", "status_field_id": "F1", "options": {}, "items": {}})
    def test_nada_a_fazer(self, mock_meta, mock_items_gql, mock_updated, tmp_path):
        from src.issues import sync_issues

        # Arquivo local sincronizado
        board_dir = tmp_path / ".pipe" / "boards" / "task" / "backlog"
        issue_file = board_dir / "42-issue.md"
        issue_file.write_text("# Issue\n\nBody\n")
        mtime = str(issue_file.stat().st_mtime)

        _write_snapshot(tmp_path, {
            "issues": {"task": [{
                "id": 42, "name": "Issue", "column": "backlog",
                "path": str(issue_file),
                "history_path": str(board_dir / "42-issue-history.md"),
                "write_path": str(board_dir / "42-issue-write.md"),
                "l-time": mtime, "b-time": "2026-06-15T10:00:00Z", "status": "ok",
            }]},
            "cache": {},
            "last_sync": "2026-06-15T10:00:00Z",
        })

        result = sync_issues(_config())

        assert result is False


class TestCicloMovimentacao:
    """Detecta movimentação local e propaga para GitHub."""

    @patch("src.issues.fetch_updated_issues", return_value=[])
    @patch("src.issues.fetch_board_items_graphql", return_value=[])
    @patch("src.issues.resolve_project_metadata", return_value={"project_id": "P1", "status_field_id": "F1", "options": {}, "items": {}})
    @patch("src.issues.move_card")
    @patch("src.issues.update_issue_body")
    @patch("src.issues.post_comment")
    @patch("src.issues._build_history", return_value=("", "2026-06-15T12:00:00Z"))
    def test_move_local_propaga(self, mock_hist, mock_comment, mock_body, mock_move,
                                mock_meta, mock_items_gql, mock_updated, tmp_path):
        from src.issues import sync_issues

        # Issue foi movida de backlog para dev
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

        result = sync_issues(_config())

        assert result is True
        mock_move.assert_called_once()
