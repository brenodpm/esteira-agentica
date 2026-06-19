"""Testes unitários para a Etapa 1: detecção de mudanças locais."""

import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

import pytest

# Patch BOARDS_DIR e SNAPSHOT_FILE antes de importar
_tmpdir = None


@pytest.fixture(autouse=True)
def setup_dirs(tmp_path, monkeypatch):
    global _tmpdir
    _tmpdir = tmp_path
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


class TestEtapa1DeteccaoLNew:
    """Arquivo local existe mas não está no snapshot → l-new."""

    def test_arquivo_novo_detectado(self, tmp_path):
        from src.issues import _etapa1_local_para_snapshot

        # Criar arquivo local
        board_dir = tmp_path / ".pipe" / "boards" / "task" / "backlog"
        issue_file = board_dir / "42-minha_issue.md"
        issue_file.write_text("# Minha Issue\n\nBody da issue\n")

        snapshot = {"issues": {"task": []}}
        _etapa1_local_para_snapshot(snapshot, _config())

        issues = snapshot["issues"]["task"]
        assert len(issues) == 1
        assert issues[0]["id"] == 42
        assert issues[0]["status"] == "l-new"
        assert issues[0]["column"] == "backlog"


class TestEtapa1DeteccaoLDel:
    """Existe no snapshot com status ok mas não existe localmente → l-del."""

    def test_arquivo_removido_detectado(self, tmp_path):
        from src.issues import _etapa1_local_para_snapshot

        snapshot = {"issues": {"task": [{
            "id": 42,
            "name": "Issue",
            "column": "backlog",
            "path": str(tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue.md"),
            "history_path": str(tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue-history.md"),
            "write_path": str(tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue-write.md"),
            "l-time": "123",
            "b-time": "2026-01-01T00:00:00Z",
            "status": "ok",
        }]}}

        _etapa1_local_para_snapshot(snapshot, _config())

        assert snapshot["issues"]["task"][0]["status"] == "l-del"


class TestEtapa1DeteccaoLSync:
    """Mtime mais novo que l-time → l-sync."""

    def test_arquivo_modificado_detectado(self, tmp_path):
        from src.issues import _etapa1_local_para_snapshot

        board_dir = tmp_path / ".pipe" / "boards" / "task" / "backlog"
        issue_file = board_dir / "42-issue.md"
        issue_file.write_text("# Issue\n\nBody modificado\n")

        # l-time antigo
        old_mtime = "0"

        snapshot = {"issues": {"task": [{
            "id": 42,
            "name": "Issue",
            "column": "backlog",
            "path": str(issue_file),
            "history_path": str(board_dir / "42-issue-history.md"),
            "write_path": str(board_dir / "42-issue-write.md"),
            "l-time": old_mtime,
            "b-time": "2026-01-01T00:00:00Z",
            "status": "ok",
        }]}}

        _etapa1_local_para_snapshot(snapshot, _config())

        assert snapshot["issues"]["task"][0]["status"] == "l-sync"

    def test_arquivo_movido_de_coluna(self, tmp_path):
        """Arquivo em coluna diferente do snapshot → l-sync + paths atualizados."""
        from src.issues import _etapa1_local_para_snapshot

        # Arquivo está em dev/ mas snapshot diz backlog
        dev_dir = tmp_path / ".pipe" / "boards" / "task" / "dev"
        issue_file = dev_dir / "42-issue.md"
        issue_file.write_text("# Issue\n\nBody\n")

        snapshot = {"issues": {"task": [{
            "id": 42,
            "name": "Issue",
            "column": "backlog",
            "path": str(tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue.md"),
            "history_path": str(tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue-history.md"),
            "write_path": str(tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue-write.md"),
            "l-time": "0",
            "b-time": "2026-01-01T00:00:00Z",
            "status": "ok",
        }]}}

        _etapa1_local_para_snapshot(snapshot, _config())

        issue = snapshot["issues"]["task"][0]
        assert issue["status"] == "l-sync"
        assert issue["column"] == "dev"
        assert "dev" in issue["path"]


class TestEtapa1OrfaoWrite:
    """Write no dir anterior com conteúdo → mesclado no novo dir."""

    def test_write_orfao_mesclado(self, tmp_path):
        from src.issues import _etapa1_local_para_snapshot

        backlog_dir = tmp_path / ".pipe" / "boards" / "task" / "backlog"
        dev_dir = tmp_path / ".pipe" / "boards" / "task" / "dev"

        # Arquivo movido para dev
        issue_file = dev_dir / "42-issue.md"
        issue_file.write_text("# Issue\n\nBody\n")

        # Write ficou em backlog (órfão)
        old_write = backlog_dir / "42-issue-write.md"
        old_write.write_text("Comentário pendente")

        snapshot = {"issues": {"task": [{
            "id": 42,
            "name": "Issue",
            "column": "backlog",
            "path": str(backlog_dir / "42-issue.md"),
            "history_path": str(backlog_dir / "42-issue-history.md"),
            "write_path": str(old_write),
            "l-time": "0",
            "b-time": "2026-01-01T00:00:00Z",
            "status": "ok",
        }]}}

        _etapa1_local_para_snapshot(snapshot, _config())

        # Write órfão deve ter sido removido
        assert not old_write.exists()
        # Novo write deve existir com conteúdo
        new_write = dev_dir / "42-issue-write.md"
        assert new_write.exists()
        assert "Comentário pendente" in new_write.read_text()
