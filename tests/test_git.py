import subprocess
from unittest.mock import patch, MagicMock
import pytest

from src.integrations.git import create_branch, commit, push, current_branch


CONFIG = {
    "gitflow": {
        "branch_base": "develop",
        "prefixes": {
            "feature": "feature/",
            "fix": "fix/",
            "release": "release/",
            "hotfix": "hotfix/",
        },
    }
}


def _mock_run(stdout=""):
    m = MagicMock()
    m.stdout = stdout
    return m


# CT-026
def test_create_branch_returns_correct_name():
    with patch("subprocess.run", return_value=_mock_run()) as mock:
        result = create_branch(CONFIG, "feature", "minha-feature")
    assert result == "feature/minha-feature"
    calls_args = [c.args[0] for c in mock.call_args_list]
    assert any("feature/minha-feature" in args for args in calls_args)


# CT-027
def test_create_branch_uses_branch_base():
    with patch("subprocess.run", return_value=_mock_run()) as mock:
        create_branch(CONFIG, "feature", "x")
    calls_args = [c.args[0] for c in mock.call_args_list]
    assert any("develop" in args for args in calls_args)


# CT-028
def test_create_branch_fix_prefix():
    with patch("subprocess.run", return_value=_mock_run()):
        result = create_branch(CONFIG, "fix", "bug-123")
    assert result == "fix/bug-123"


# CT-029
def test_commit_no_files_uses_add_all():
    with patch("subprocess.run", return_value=_mock_run()) as mock:
        commit(CONFIG, "feat: inicial", files=None)
    calls_args = [c.args[0] for c in mock.call_args_list]
    assert any(args == ["git", "add", "-A"] for args in calls_args)
    assert any("feat: inicial" in args for args in calls_args)


# CT-030
def test_commit_with_files_adds_only_listed():
    with patch("subprocess.run", return_value=_mock_run()) as mock:
        commit(CONFIG, "fix: ajuste", files=["src/foo.py", "src/bar.py"])
    calls_args = [c.args[0] for c in mock.call_args_list]
    add_call = next(args for args in calls_args if args[1] == "add")
    assert "src/foo.py" in add_call
    assert "src/bar.py" in add_call
    assert "-A" not in add_call


# CT-031
def test_push_calls_correct_command():
    with patch("subprocess.run", return_value=_mock_run()) as mock:
        push("feature/minha-feature")
    calls_args = [c.args[0] for c in mock.call_args_list]
    assert any(
        args == ["git", "push", "-u", "origin", "feature/minha-feature"]
        for args in calls_args
    )


# CT-032
def test_current_branch_returns_stripped_name():
    with patch("subprocess.run", return_value=_mock_run("feature/minha-feature\n")):
        result = current_branch()
    assert result == "feature/minha-feature"


# CT-033
def test_git_error_raises_runtime_error():
    err = subprocess.CalledProcessError(1, "git", stderr="fatal: not a git repo")
    with patch("subprocess.run", side_effect=err):
        with pytest.raises(RuntimeError, match="fatal: not a git repo"):
            push("feature/x")


# CT-034
def test_public_imports_are_callable():
    from src.integrations.git import create_branch, commit, push, current_branch
    assert callable(create_branch)
    assert callable(commit)
    assert callable(push)
    assert callable(current_branch)
