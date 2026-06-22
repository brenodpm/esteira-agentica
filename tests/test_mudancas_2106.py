"""Testes para mudanças de 21/06: pick_task parallel, sync_issues_local, full_sync penalty, etapa3."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture(autouse=True)
def setup_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr("src.issues.BOARDS_DIR", tmp_path / ".pipe" / "boards")
    monkeypatch.setattr("src.issues.PIPE_DIR", tmp_path / ".pipe")
    monkeypatch.setattr("src.issues.SNAPSHOT_FILE", tmp_path / ".pipe" / "snapshot.json")
    monkeypatch.setattr("src.pick_task.BOARDS_DIR", tmp_path / ".pipe" / "boards")
    monkeypatch.setattr("src.pick_task.SNAPSHOT_FILE", tmp_path / ".pipe" / "snapshot.json")
    (tmp_path / ".pipe").mkdir()
    (tmp_path / ".pipe" / "boards" / "epic" / "backlog").mkdir(parents=True)
    (tmp_path / ".pipe" / "boards" / "epic" / "analise").mkdir(parents=True)
    (tmp_path / ".pipe" / "boards" / "epic" / "aprovacao").mkdir(parents=True)
    (tmp_path / ".pipe" / "boards" / "epic" / "encerrado").mkdir(parents=True)
    (tmp_path / ".pipe" / "boards" / "epic" / "cancelado").mkdir(parents=True)
    (tmp_path / ".pipe" / "boards" / "task" / "backlog").mkdir(parents=True)
    (tmp_path / ".pipe" / "boards" / "task" / "dev").mkdir(parents=True)


def _config():
    return {
        "repo": "owner/repo",
        "boards": {
            "epic": {
                "name": "Epics",
                "todo": "backlog",
                "priority": 4,
                "parallel": False,
                "columns": {
                    "backlog": {"name": "Backlog", "change": {"advance": "analise"}},
                    "analise": {"name": "Análise", "agent": "product", "change": {"advance": "aprovacao"}},
                    "aprovacao": {"name": "Aprovação"},
                    "encerrado": {"name": "Encerrado"},
                    "cancelado": {"name": "Cancelado"},
                },
            },
            "task": {
                "name": "Tasks",
                "todo": "backlog",
                "priority": 2,
                "columns": {
                    "backlog": {"name": "Backlog", "change": {"advance": "dev"}},
                    "dev": {"name": "Desenvolvimento", "agent": "engineering", "change": {"advance": "done"}},
                },
            },
        },
        "boards_meta": {"create-remote-boards": False, "allow-del-remote-issue": False},
    }


def _write_snapshot(tmp_path, data):
    (tmp_path / ".pipe" / "snapshot.json").write_text(json.dumps(data))


# ══════════════════════════════════════════════════════════════════════════════
# pick_task com parallel: false
# ══════════════════════════════════════════════════════════════════════════════


class TestPickTaskParallel:
    """pick_task deve bloquear auto-advance em boards com parallel: false se há issue ativa."""

    def test_bloqueia_auto_advance_com_issue_ativa(self, tmp_path):
        """Board epic com issue em 'aprovacao' (ativa) → não faz auto-advance do #4 no backlog."""
        from src.pick_task import pick_task

        task_file = tmp_path / ".pipe" / "boards" / "task" / "dev" / "99-task.md"
        task_file.write_text("# Task\n\nBody\n")

        _write_snapshot(tmp_path, {"issues": {
            "epic": [
                {"id": 2, "column": "aprovacao", "status": "ok",
                 "path": str(tmp_path / ".pipe" / "boards" / "epic" / "aprovacao" / "2-epic.md"),
                 "history_path": "", "write_path": "", "created_at": "2026-01-01"},
                {"id": 4, "column": "backlog", "status": "ok",
                 "path": str(tmp_path / ".pipe" / "boards" / "epic" / "backlog" / "4-epic.md"),
                 "history_path": "", "write_path": "", "created_at": "2026-01-02"},
            ],
            "task": [
                {"id": 99, "column": "dev", "status": "ok",
                 "path": str(task_file),
                 "history_path": "", "write_path": "", "created_at": "2026-01-01"},
            ],
        }})

        result = pick_task(_config())
        # Epic #4 não pode auto-advance (parallel:false + #2 ativa)
        # Mas task board é processado normalmente
        assert result is not None
        assert result["id"] == 99
        assert result["board_id"] == "task"

    def test_issue_ativa_ainda_e_processada(self, tmp_path):
        """Board epic com parallel:false — issue já fora do backlog é processada normalmente."""
        from src.pick_task import pick_task

        analise_file = tmp_path / ".pipe" / "boards" / "epic" / "analise" / "2-epic.md"
        analise_file.write_text("# Epic 2\n\nBody\n")

        _write_snapshot(tmp_path, {"issues": {
            "epic": [
                {"id": 2, "column": "analise", "status": "ok",
                 "path": str(analise_file),
                 "history_path": "", "write_path": "", "created_at": "2026-01-01"},
                {"id": 4, "column": "backlog", "status": "ok",
                 "path": str(tmp_path / ".pipe" / "boards" / "epic" / "backlog" / "4-epic.md"),
                 "history_path": "", "write_path": "", "created_at": "2026-01-02"},
            ],
            "task": [],
        }})

        result = pick_task(_config())
        # Issue #2 em analise (tem agent + change.advance) deve ser selecionada
        assert result is not None
        assert result["id"] == 2
        assert result["board_id"] == "epic"

    def test_permite_board_sem_issue_ativa(self, tmp_path):
        """Board epic com issues apenas em backlog/encerrado → permite seleção."""
        from src.pick_task import pick_task

        epic_file = tmp_path / ".pipe" / "boards" / "epic" / "backlog" / "4-epic.md"
        epic_file.write_text("# Epic\n\nBody\n")
        history_file = tmp_path / ".pipe" / "boards" / "epic" / "backlog" / "4-epic-history.md"
        history_file.write_text("")
        write_file = tmp_path / ".pipe" / "boards" / "epic" / "backlog" / "4-epic-write.md"
        write_file.write_text("")

        _write_snapshot(tmp_path, {"issues": {
            "epic": [
                {"id": 3, "column": "encerrado", "status": "ok",
                 "path": str(tmp_path / ".pipe" / "boards" / "epic" / "encerrado" / "3-epic.md"),
                 "history_path": str(tmp_path / ".pipe" / "boards" / "epic" / "encerrado" / "3-epic-history.md"),
                 "write_path": str(tmp_path / ".pipe" / "boards" / "epic" / "encerrado" / "3-epic-write.md"),
                 "created_at": "2026-01-01"},
                {"id": 4, "column": "backlog", "status": "ok",
                 "path": str(epic_file),
                 "history_path": str(history_file),
                 "write_path": str(write_file),
                 "created_at": "2026-01-02"},
            ],
            "task": [],
        }})

        from src.pick_task import TODO_ADVANCE
        result = pick_task(_config())
        # Deve fazer auto-advance do #4 (backlog → analise)
        assert result == TODO_ADVANCE

    def test_bloqueada_conta_como_ativa_para_auto_advance(self, tmp_path):
        """Issue bloqueada em coluna não-terminal conta como ativa → bloqueia auto-advance do backlog."""
        from src.pick_task import pick_task

        blocked_file = tmp_path / ".pipe" / "boards" / "epic" / "analise" / "2-epic.md"
        blocked_file.write_text("# Epic\n\n/blocked_by 1\n")

        _write_snapshot(tmp_path, {"issues": {
            "epic": [
                {"id": 2, "column": "analise", "status": "ok",
                 "path": str(blocked_file),
                 "history_path": "", "write_path": "", "created_at": "2026-01-01"},
                {"id": 4, "column": "backlog", "status": "ok",
                 "path": str(tmp_path / ".pipe" / "boards" / "epic" / "backlog" / "4-epic.md"),
                 "history_path": "", "write_path": "", "created_at": "2026-01-02"},
            ],
            "task": [],
        }})

        result = pick_task(_config())
        # #2 é bloqueada (pula por _is_blocked), #4 no backlog não pode auto-advance → None
        assert result is None

    def test_board_sem_parallel_nao_afetado(self, tmp_path):
        """Board task (sem parallel: false) seleciona normalmente com múltiplas issues."""
        from src.pick_task import pick_task

        task1 = tmp_path / ".pipe" / "boards" / "task" / "dev" / "10-task1.md"
        task1.write_text("# Task 1\n\nBody\n")
        task2 = tmp_path / ".pipe" / "boards" / "task" / "dev" / "11-task2.md"
        task2.write_text("# Task 2\n\nBody\n")

        _write_snapshot(tmp_path, {"issues": {
            "epic": [],
            "task": [
                {"id": 10, "column": "dev", "status": "ok",
                 "path": str(task1),
                 "history_path": "", "write_path": "", "created_at": "2026-01-01"},
                {"id": 11, "column": "dev", "status": "ok",
                 "path": str(task2),
                 "history_path": "", "write_path": "", "created_at": "2026-01-02"},
            ],
        }})

        result = pick_task(_config())
        # Seleciona a mais antiga normalmente
        assert result is not None
        assert result["id"] == 10


# ══════════════════════════════════════════════════════════════════════════════
# sync_issues_local (nova função)
# ══════════════════════════════════════════════════════════════════════════════


class TestSyncIssuesLocal:
    """sync_issues_local executa apenas etapas 1 e 4 (sem GitHub)."""

    def test_detecta_mudanca_local_sem_chamar_github(self, tmp_path):
        """Detecta l-new e processa b-del sem chamadas GitHub."""
        from src.issues import sync_issues_local

        # Criar arquivo novo local
        board_dir = tmp_path / ".pipe" / "boards" / "task" / "backlog"
        (board_dir / "0-nova.md").write_text("# Nova\n\nBody\n")

        _write_snapshot(tmp_path, {
            "issues": {"task": [], "epic": []},
            "cache": {},
            "last_sync": "2026-06-21T10:00:00Z",
        })

        result = sync_issues_local(_config())
        # Não houve b-del nem b-new no snapshot, mas etapa 1 detectou l-new
        # sync_issues_local retorna count de etapa 4 apenas
        assert result is False  # etapa 4 count == 0

        # Verifica que etapa 1 rodou (l-new detectado no snapshot)
        snapshot = json.loads((tmp_path / ".pipe" / "snapshot.json").read_text())
        task_issues = snapshot["issues"]["task"]
        assert len(task_issues) == 1
        assert task_issues[0]["status"] == "l-new"

    @patch("src.issues._build_history", return_value=("", "2026-01-01T00:00:00Z"))
    def test_processa_b_new_localmente(self, mock_hist, tmp_path):
        """b-new cria arquivos locais sem chamar GitHub (exceto history)."""
        from src.issues import sync_issues_local

        _write_snapshot(tmp_path, {
            "issues": {"task": [{
                "id": 55, "name": "Remote Issue", "column": "backlog",
                "path": None, "history_path": None, "write_path": None,
                "l-time": None, "b-time": "2026-01-01T00:00:00Z",
                "created_at": None, "status": "b-new",
                "_body": "Body from remote",
            }], "epic": []},
            "cache": {},
            "last_sync": "2026-06-21T10:00:00Z",
        })

        result = sync_issues_local(_config())
        assert result is True

        snapshot = json.loads((tmp_path / ".pipe" / "snapshot.json").read_text())
        issue = snapshot["issues"]["task"][0]
        assert issue["status"] == "ok"
        assert Path(issue["path"]).exists()


# ══════════════════════════════════════════════════════════════════════════════
# full_sync com penalty ativo
# ══════════════════════════════════════════════════════════════════════════════


class TestFullSyncPenalty:
    """full_sync deve pular quando penalty está ativo."""

    @patch("src.sync.is_in_penalty", return_value=True)
    @patch("src.sync.resolve_project_metadata")
    def test_full_sync_pula_com_penalty(self, mock_meta, mock_penalty, tmp_path):
        from src.sync import full_sync

        snapshot = {"issues": {}, "cache": {}, "last_sync": "2026-06-21T10:00:00Z"}
        full_sync(_config(), snapshot)

        # Não deve chamar resolve_project_metadata
        mock_meta.assert_not_called()

    @patch("src.sync.is_in_penalty", return_value=False)
    @patch("src.sync.fetch_board_items_graphql", return_value=[])
    @patch("src.sync.resolve_project_metadata", return_value={"project_id": "P1", "status_field_id": "F1", "options": {}, "items": {}})
    def test_full_sync_executa_sem_penalty(self, mock_meta, mock_items, mock_penalty, tmp_path):
        from src.sync import full_sync

        snapshot = {"issues": {"epic": [], "task": []}, "cache": {}, "last_sync": "2026-06-21T10:00:00Z"}
        full_sync(_config(), snapshot)

        # Deve ter chamado resolve para cada board
        assert mock_meta.call_count == 2


# ══════════════════════════════════════════════════════════════════════════════
# _etapa3 sem deleted_this_cycle (parâmetro removido)
# ══════════════════════════════════════════════════════════════════════════════


class TestEtapa3SemDeleted:
    """_etapa3 não recebe mais deleted_this_cycle e não cria b-new inline."""

    @patch("src.issues.fetch_updated_issues", return_value=[42])
    @patch("src.issues.fetch_board_items_graphql", return_value=[
        {"item_id": "PVTI_1", "number": 42, "title": "Issue", "url": "", "body": "Updated", "status": "Backlog", "updated_at": "2026-06-21T12:00:00Z"},
        {"item_id": "PVTI_2", "number": 99, "title": "Nova", "url": "", "body": "Body", "status": "Backlog", "updated_at": "2026-06-21T12:00:00Z"},
    ])
    @patch("src.issues.resolve_project_metadata", return_value={"project_id": "P1", "status_field_id": "F1", "options": {}, "items": {}})
    @patch("src.issues.fetch_issue_comments", return_value={"updatedAt": "2026-06-21T12:00:00Z", "comments": []})
    def test_nao_cria_b_new_inline(self, mock_comments, mock_meta, mock_items, mock_updated, tmp_path):
        """Etapa 3 não deve mais criar b-new para issues remotas desconhecidas."""
        from src.issues import _etapa3_github_para_snapshot

        issue_file = tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue.md"
        issue_file.write_text("# Issue\n\nBody\n")

        snapshot = {
            "issues": {"task": [{
                "id": 42, "name": "Issue", "column": "backlog",
                "path": str(issue_file),
                "history_path": str(tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue-history.md"),
                "write_path": str(tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue-write.md"),
                "l-time": str(issue_file.stat().st_mtime), "b-time": "2026-06-21T10:00:00Z", "status": "ok",
            }]},
            "cache": {},
            "last_sync": "2026-06-21T10:00:00Z",
        }

        count = _etapa3_github_para_snapshot(snapshot, _config())

        # Deve ter sincronizado #42 (body update)
        assert count == 1
        # NÃO deve ter criado b-new para #99
        assert len(snapshot["issues"]["task"]) == 1
        assert all(i["id"] != 99 for i in snapshot["issues"]["task"])

    @patch("src.issues.fetch_updated_issues", return_value=[50])
    @patch("src.issues.fetch_board_items_graphql", return_value=[])
    @patch("src.issues.resolve_project_metadata", return_value={"project_id": "P1", "status_field_id": "F1", "options": {}, "items": {}})
    def test_skip_board_sem_issues_atualizadas(self, mock_meta, mock_items, mock_updated, tmp_path):
        """Etapa 3 pula boards que não têm issues atualizadas (otimização)."""
        from src.issues import _etapa3_github_para_snapshot

        snapshot = {
            "issues": {"task": [{
                "id": 42, "name": "Issue", "column": "backlog",
                "path": str(tmp_path / ".pipe" / "boards" / "task" / "backlog" / "42-issue.md"),
                "history_path": "", "write_path": "",
                "l-time": "0", "b-time": "2026-06-21T10:00:00Z", "status": "ok",
            }]},
            "cache": {},
            "last_sync": "2026-06-21T10:00:00Z",
        }

        count = _etapa3_github_para_snapshot(snapshot, _config())

        # #50 não está no board task → não chama GraphQL
        assert count == 0
        mock_items.assert_not_called()
