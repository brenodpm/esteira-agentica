import pytest
from pathlib import Path
from src.config import load


def _write_yaml(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "esteira.yml"
    p.write_text(content)
    return p


_MINIMAL = """\
doc: docs/
git:
  repo: "owner/repo"
boards:
  task:
    name: Tasks
    todo: backlog
    columns:
      backlog:
        name: Backlog
      done:
        name: Done
"""

_FULL = """\
doc: docs/
git:
  repo: "owner/repo"
  flow:
    base: main
    feature:
      prefix: feat
      description: Feature branch
      create: main
      merge: main
boards:
  task:
    name: Tasks
    todo: backlog
    columns:
      backlog:
        name: Backlog
      done:
        name: Done
pipe:
  agent:
    timeout: 30
    sleeptime: 5
"""


def test_load_full_config(tmp_path):
    cfg = load(_write_yaml(tmp_path, _FULL))
    assert cfg["repo"] == "owner/repo"
    assert cfg["doc"] == "docs/"
    assert "task" in cfg["boards"]
    assert cfg["gitflow"]["branch_base"] == "main"
    assert cfg["pipe"]["timeout"] == 30
    assert cfg["pipe"]["sleeptime"] == 5


def test_load_applies_default_branch_base(tmp_path):
    cfg = load(_write_yaml(tmp_path, _MINIMAL))
    assert cfg["gitflow"]["branch_base"] == "main"


def test_load_applies_default_pipe_values(tmp_path):
    cfg = load(_write_yaml(tmp_path, _MINIMAL))
    assert cfg["pipe"]["timeout"] is None
    assert cfg["pipe"]["sleeptime"] is None


def test_load_applies_default_board_priority(tmp_path):
    cfg = load(_write_yaml(tmp_path, _MINIMAL))
    for board in cfg["boards"].values():
        assert board["priority"] == 0


def test_load_has_no_agents_sequence(tmp_path):
    cfg = load(_write_yaml(tmp_path, _MINIMAL))
    assert "agents_sequence" not in cfg


def test_load_raises_when_repo_missing(tmp_path):
    content = "doc: docs/\nboards:\n  t:\n    name: T\n    todo: b\n    columns:\n      b:\n        name: B\n"
    with pytest.raises(ValueError, match="git.repo"):
        load(_write_yaml(tmp_path, content))


def test_load_raises_when_doc_missing(tmp_path):
    content = "git:\n  repo: owner/repo\nboards:\n  t:\n    name: T\n    todo: b\n    columns:\n      b:\n        name: B\n"
    with pytest.raises(ValueError, match="doc"):
        load(_write_yaml(tmp_path, content))


def test_load_raises_when_boards_missing(tmp_path):
    content = "doc: docs/\ngit:\n  repo: owner/repo\n"
    with pytest.raises(ValueError, match="boards"):
        load(_write_yaml(tmp_path, content))


def test_load_raises_when_repo_empty(tmp_path):
    content = _MINIMAL.replace('"owner/repo"', '""')
    with pytest.raises(ValueError, match="git.repo"):
        load(_write_yaml(tmp_path, content))


def test_load_is_importable():
    assert callable(load)
