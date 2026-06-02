import subprocess
from unittest.mock import patch, MagicMock
import pytest

from src.agents import run


def _mock_result(stdout="artefato gerado", returncode=0):
    m = MagicMock()
    m.stdout = stdout
    m.stderr = ""
    m.returncode = returncode
    return m


# CT-043 — run retorna dict com output e duration_s preenchidos
def test_run_returns_dict():
    with patch("subprocess.run", return_value=_mock_result()) as mock_sub:
        result = run(role="requirements", context_files=[], prompt="gere requisitos")
    assert isinstance(result, dict)
    assert result["output"] == "artefato gerado"
    assert isinstance(result["duration_s"], float)
    assert result["duration_s"] >= 0
    assert result["tokens_in"] is None or isinstance(result["tokens_in"], int)
    assert result["tokens_out"] is None or isinstance(result["tokens_out"], int)


# CT-044 — tokens_in e tokens_out são None quando CLI não os expõe
def test_run_tokens_none_when_not_exposed():
    with patch("subprocess.run", return_value=_mock_result(stdout="sem tokens")):
        result = run(role="requirements", context_files=[], prompt="x")
    assert result["tokens_in"] is None
    assert result["tokens_out"] is None


# CT-045 — run lança TimeoutError quando processo excede timeout
def test_run_raises_timeout():
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="kiro", timeout=10)):
        with pytest.raises(TimeoutError) as exc_info:
            run(role="engineering", context_files=[], prompt="x", timeout_s=10)
    assert "engineering" in str(exc_info.value)
    assert "10" in str(exc_info.value)


# CT-046 — run lança RuntimeError quando código de saída é não-zero
def test_run_raises_runtime_error_on_nonzero():
    err = subprocess.CalledProcessError(returncode=1, cmd="kiro", stderr="falha grave")
    with patch("subprocess.run", side_effect=err):
        with pytest.raises(RuntimeError) as exc_info:
            run(role="quality", context_files=[], prompt="x")
    assert "falha grave" in str(exc_info.value)


# CT-048 — run acessível via src.agents
def test_public_interface():
    from src.agents import run
    assert callable(run)
