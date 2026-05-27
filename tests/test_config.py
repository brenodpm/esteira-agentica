import json
import pytest
from pathlib import Path
from src.config import load


def _write_json(tmp_path: Path, data: dict) -> Path:
    p = tmp_path / "project.json"
    p.write_text(json.dumps(data))
    return p


def test_load_full_config(tmp_path):
    cfg_file = _write_json(tmp_path, {
        "repo": "owner/repo",
        "gitflow": {"branch_base": "main", "prefixes": {"feature": "feat/"}},
        "board": {"columns": ["Todo", "Done"], "labels": {"bug": "red"}},
        "agents_sequence": ["agent_a"],
    })
    cfg = load(cfg_file)
    assert isinstance(cfg, dict)
    assert cfg["repo"] == "owner/repo"
    assert cfg["gitflow"]["branch_base"] == "main"
    assert cfg["gitflow"]["prefixes"] == {"feature": "feat/"}
    assert cfg["board"]["columns"] == ["Todo", "Done"]
    assert cfg["board"]["labels"] == {"bug": "red"}
    assert cfg["agents_sequence"] == ["agent_a"]


def test_load_applies_default_branch_base(tmp_path):
    cfg = load(_write_json(tmp_path, {"repo": "owner/repo"}))
    assert cfg["gitflow"]["branch_base"] == "develop"


def test_load_applies_default_prefixes(tmp_path):
    cfg = load(_write_json(tmp_path, {"repo": "owner/repo"}))
    assert cfg["gitflow"]["prefixes"]["feature"] == "feature/"
    assert cfg["gitflow"]["prefixes"]["fix"] == "fix/"
    assert cfg["gitflow"]["prefixes"]["release"] == "release/"
    assert cfg["gitflow"]["prefixes"]["hotfix"] == "hotfix/"


def test_load_applies_default_board_columns(tmp_path):
    cfg = load(_write_json(tmp_path, {"repo": "owner/repo"}))
    assert cfg["board"]["columns"] == ["Backlog", "In Progress", "Done"]


def test_load_applies_default_board_labels(tmp_path):
    cfg = load(_write_json(tmp_path, {"repo": "owner/repo"}))
    assert cfg["board"]["labels"] == {}


def test_load_applies_default_agents_sequence(tmp_path):
    cfg = load(_write_json(tmp_path, {"repo": "owner/repo"}))
    assert isinstance(cfg["agents_sequence"], list)
    assert len(cfg["agents_sequence"]) > 0


def test_load_raises_value_error_when_repo_missing(tmp_path):
    with pytest.raises(ValueError, match="repo"):
        load(_write_json(tmp_path, {}))


def test_load_raises_value_error_when_repo_empty(tmp_path):
    with pytest.raises(ValueError, match="repo"):
        load(_write_json(tmp_path, {"repo": ""}))


def test_load_is_importable():
    assert callable(load)
