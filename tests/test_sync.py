from unittest.mock import patch, call
import pytest

from src.integrations.github.sync import sync_boards

_CONFIG = {
    "repo": "org/repo",
    "boards": {
        "task": {
            "name": "Tasks",
            "columns": {
                "backlog": {"name": "Backlog"},
                "dev": {"name": "Dev"},
                "concluido": {"name": "Concluído"},
            },
        }
    },
}

_OWNER_ID = "O_owner123"
_PROJECT = {"id": "PVT_proj1", "number": 1, "title": "Tasks"}
_FIELD = {"id": "F_field1", "name": "Status", "options": [{"id": "O1", "name": "Backlog"}]}


# CT-098 — sync cria projeto quando não existe
def test_sync_creates_project():
    with patch("src.integrations.github.sync._owner_id", return_value=(_OWNER_ID, "organization")), \
         patch("src.integrations.github.sync._list_projects", return_value=[]), \
         patch("src.integrations.github.sync._create_project", return_value=_PROJECT) as mock_create, \
         patch("src.integrations.github.sync._get_status_field", return_value=_FIELD), \
         patch("src.integrations.github.sync._add_status_option"):
        sync_boards(_CONFIG)
    mock_create.assert_called_once_with(_OWNER_ID, "Tasks")


# CT-099 — sync não cria projeto quando já existe
def test_sync_skips_existing_project():
    with patch("src.integrations.github.sync._owner_id", return_value=(_OWNER_ID, "organization")), \
         patch("src.integrations.github.sync._list_projects", return_value=[_PROJECT]), \
         patch("src.integrations.github.sync._create_project") as mock_create, \
         patch("src.integrations.github.sync._get_status_field", return_value=_FIELD), \
         patch("src.integrations.github.sync._add_status_option"):
        sync_boards(_CONFIG)
    mock_create.assert_not_called()


# CT-100 — sync cria campo Status quando não existe
def test_sync_creates_status_field():
    with patch("src.integrations.github.sync._owner_id", return_value=(_OWNER_ID, "organization")), \
         patch("src.integrations.github.sync._list_projects", return_value=[_PROJECT]), \
         patch("src.integrations.github.sync._get_status_field", return_value=None), \
         patch("src.integrations.github.sync._create_status_field", return_value=_FIELD) as mock_field, \
         patch("src.integrations.github.sync._add_status_option"):
        sync_boards(_CONFIG)
    mock_field.assert_called_once_with(_PROJECT["id"])


# CT-101 — sync adiciona apenas colunas ausentes, não duplica existentes
def test_sync_adds_only_missing_columns():
    # Backlog já existe; Dev e Concluído são novos
    with patch("src.integrations.github.sync._owner_id", return_value=(_OWNER_ID, "organization")), \
         patch("src.integrations.github.sync._list_projects", return_value=[_PROJECT]), \
         patch("src.integrations.github.sync._get_status_field", return_value=_FIELD), \
         patch("src.integrations.github.sync._add_status_option") as mock_add:
        sync_boards(_CONFIG)
    added_names = [c.args[2] for c in mock_add.call_args_list]
    assert "Dev" in added_names
    assert "Concluído" in added_names
    assert "Backlog" not in added_names


# CT-102 — sync não faz nada quando boards está vazio
def test_sync_empty_boards(capsys):
    sync_boards({"repo": "org/repo", "boards": {}})
    assert "Nenhum board" in capsys.readouterr().out


# CT-103 — sync processa múltiplos boards
def test_sync_multiple_boards():
    config = {
        "repo": "org/repo",
        "boards": {
            "a": {"name": "Board A", "columns": {"c1": {"name": "Col1"}}},
            "b": {"name": "Board B", "columns": {"c2": {"name": "Col2"}}},
        },
    }
    proj_a = {"id": "PVT_a", "number": 1, "title": "Board A"}
    proj_b = {"id": "PVT_b", "number": 2, "title": "Board B"}
    field = {"id": "F1", "name": "Status", "options": []}

    with patch("src.integrations.github.sync._owner_id", return_value=(_OWNER_ID, "user")), \
         patch("src.integrations.github.sync._list_projects", return_value=[proj_a, proj_b]), \
         patch("src.integrations.github.sync._get_status_field", return_value=field), \
         patch("src.integrations.github.sync._add_status_option") as mock_add:
        sync_boards(config)
    assert mock_add.call_count == 2
