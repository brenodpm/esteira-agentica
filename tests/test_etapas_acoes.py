"""Testes unitários para ações das etapas 2, 3 e 4."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture(autouse=True)
def setup_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr("src.issues.BOARDS_DIR", tmp_path / ".pipe" / "boards")
    monkeypatch.setattr("src.issues.PIPE_DIR", tmp_path / ".pipe")
    monkeypatch.setattr("src.issues.SNAPSHOT_FILE", tmp_path / ".pipe" / "snapshot.json")
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


class TestEtapa2LSync:
    """Etapa 2: l-sync propaga mudanças para GitHub."""

    @patch("src.issues.move_card")
    @patch("src.issues.update_issue_body")
    @patch("src.issues.post_comment")
    @patch("src.issues._build_history", return_value=("history", "2026-01-01T00:00:00Z"))
    def test_l_sync_move_e_atualiza(self, mock_hist, mock_comment, mock_body, mock_move, tmp_path):
        from src.issues import _etapa2_snapshot_para_github

        board_dir = tmp_path / ".pipe" / "boards" / "task" / "dev"
        issue_file = board_dir / "42-issue.md"
        issue_file.write_text("# Issue\n\nNovo body\n")
        write_file = board_dir / "42-issue-write.md"
        write_file.write_text("")

        snapshot = {"issues": {"task": [{
            "id": 42, "name": "Issue", "column": "dev",
            "path": str(issue_file),
            "history_path": str(board_dir / "42-issue-history.md"),
            "write_path": str(write_file),
            "l-time": "999", "b-time": "2025-01-01T00:00:00Z", "status": "l-sync",
        }]}, "cache": {}}

        count = _etapa2_snapshot_para_github(snapshot, _config())

        assert count == 1
        mock_move.assert_called_once()
        mock_body.assert_called_once()
        assert snapshot["issues"]["task"][0]["status"] == "ok"

    @patch("src.issues.move_card")
    @patch("src.issues.update_issue_body")
    @patch("src.issues.post_comment")
    @patch("src.issues._build_history", return_value=("", ""))
    def test_l_sync_posta_write(self, mock_hist, mock_comment, mock_body, mock_move, tmp_path):
        from src.issues import _etapa2_snapshot_para_github

        board_dir = tmp_path / ".pipe" / "boards" / "task" / "backlog"
        issue_file = board_dir / "42-issue.md"
        issue_file.write_text("# Issue\n\nBody\n")
        write_file = board_dir / "42-issue-write.md"
        write_file.write_text("Comentário a postar")

        snapshot = {"issues": {"task": [{
            "id": 42, "name": "Issue", "column": "backlog",
            "path": str(issue_file),
            "history_path": str(board_dir / "42-issue-history.md"),
            "write_path": str(write_file),
            "l-time": "999", "b-time": "2025-01-01T00:00:00Z", "status": "l-sync",
        }]}, "cache": {}}

        _etapa2_snapshot_para_github(snapshot, _config())

        mock_comment.assert_called_once_with("owner/repo", 42, "Comentário a postar")
        assert write_file.read_text() == ""


class TestEtapa2LNew:
    """Etapa 2: l-new cria issue no GitHub."""

    @patch("src.issues.move_card")
    @patch("src.issues.add_issue_to_project", return_value="PVTI_item123")
    @patch("src.issues.get_issue_node_id", return_value="I_node123")
    @patch("src.issues.create_issue", return_value=99)
    def test_l_new_cria_issue(self, mock_create, mock_node, mock_add, mock_move, tmp_path):
        from src.issues import _etapa2_snapshot_para_github

        board_dir = tmp_path / ".pipe" / "boards" / "task" / "backlog"
        issue_file = board_dir / "0-nova_issue.md"
        issue_file.write_text("# Nova Issue\n\nBody novo\n")

        snapshot = {"issues": {"task": [{
            "id": 0, "name": "Nova Issue", "column": "backlog",
            "path": str(issue_file),
            "history_path": str(board_dir / "0-nova_issue-history.md"),
            "write_path": str(board_dir / "0-nova_issue-write.md"),
            "l-time": "999", "b-time": None, "status": "l-new",
        }]}, "cache": {}}

        count = _etapa2_snapshot_para_github(snapshot, _config())

        assert count == 1
        mock_create.assert_called_once_with("owner/repo", "Nova Issue", "Body novo")
        assert snapshot["issues"]["task"][0]["id"] == 99
        assert snapshot["issues"]["task"][0]["status"] == "ok"


class TestEtapa2LDel:
    """Etapa 2: l-del com allow-del-remote-issue."""

    @patch("src.issues.close_issue")
    @patch("src.issues.post_comment")
    def test_l_del_com_permissao(self, mock_comment, mock_close, tmp_path):
        from src.issues import _etapa2_snapshot_para_github

        config = _config()
        config["boards_meta"]["allow-del-remote-issue"] = True

        board_dir = tmp_path / ".pipe" / "boards" / "task" / "backlog"
        issue_file = board_dir / "42-issue.md"
        issue_file.write_text("# Issue\n\nBody\n")

        snapshot = {"issues": {"task": [{
            "id": 42, "name": "Issue", "column": "backlog",
            "path": str(issue_file),
            "history_path": str(board_dir / "42-issue-history.md"),
            "write_path": str(board_dir / "42-issue-write.md"),
            "l-time": "999", "b-time": "2025-01-01T00:00:00Z", "status": "l-del",
        }]}, "cache": {}}

        count = _etapa2_snapshot_para_github(snapshot, config)

        assert count == 1
        mock_comment.assert_called_once()
        mock_close.assert_called_once_with("owner/repo", 42)
        assert len(snapshot["issues"]["task"]) == 0

    @patch("src.issues.close_issue")
    @patch("src.issues.post_comment")
    def test_l_del_sem_permissao(self, mock_comment, mock_close, tmp_path):
        from src.issues import _etapa2_snapshot_para_github

        config = _config()
        config["boards_meta"]["allow-del-remote-issue"] = False

        snapshot = {"issues": {"task": [{
            "id": 42, "name": "Issue", "column": "backlog",
            "path": str(tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue.md"),
            "history_path": str(tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue-history.md"),
            "write_path": str(tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue-write.md"),
            "l-time": "999", "b-time": "2025-01-01T00:00:00Z", "status": "l-del",
        }]}, "cache": {}}

        count = _etapa2_snapshot_para_github(snapshot, config)

        assert count == 1
        mock_close.assert_not_called()
        assert len(snapshot["issues"]["task"]) == 0


class TestEtapa4BDel:
    """Etapa 4: b-del remove arquivos locais."""

    def test_b_del_remove_arquivos(self, tmp_path):
        from src.issues import _etapa4_residuos

        board_dir = tmp_path / ".pipe" / "boards" / "task" / "backlog"
        issue_file = board_dir / "42-issue.md"
        issue_file.write_text("# Issue\n")
        history_file = board_dir / "42-issue-history.md"
        history_file.write_text("")
        write_file = board_dir / "42-issue-write.md"
        write_file.write_text("")

        snapshot = {"issues": {"task": [{
            "id": 42, "name": "Issue", "column": "backlog",
            "path": str(issue_file),
            "history_path": str(history_file),
            "write_path": str(write_file),
            "l-time": "999", "b-time": "2025-01-01T00:00:00Z", "status": "b-del",
        }]}}

        count = _etapa4_residuos(snapshot, _config())

        assert count == 1
        assert not issue_file.exists()
        assert not history_file.exists()
        assert not write_file.exists()
        assert len(snapshot["issues"]["task"]) == 0


class TestEtapa4BNew:
    """Etapa 4: b-new cria arquivos locais."""

    @patch("src.issues._build_history", return_value=("hist content", "2026-01-01T00:00:00Z"))
    def test_b_new_cria_arquivos(self, mock_hist, tmp_path):
        from src.issues import _etapa4_residuos

        snapshot = {"issues": {"task": [{
            "id": 55, "name": "Nova do Board", "column": "backlog",
            "path": None, "history_path": None, "write_path": None,
            "l-time": None, "b-time": "2026-01-01T00:00:00Z", "status": "b-new",
            "created_at": None,
        }]}}

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout='{"body": "Body remoto"}')
            count = _etapa4_residuos(snapshot, _config())

        assert count == 1
        issue = snapshot["issues"]["task"][0]
        assert issue["status"] == "ok"
        assert Path(issue["path"]).exists()
        assert "Nova do Board" in Path(issue["path"]).read_text()
