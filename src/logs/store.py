"""Log estruturado de execução da esteira.

Arquivos:
  logs/esteira-YYYY-MM-DD.jsonl  — eventos estruturados (um por linha)
  logs/output-YYYY-MM-DD.log     — outputs brutos dos agentes
"""
import json
from datetime import datetime, timezone
from pathlib import Path

_LOG_DIR = Path("logs")


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log_path() -> Path:
    return _LOG_DIR / f"esteira-{_today()}.jsonl"


def _output_path() -> Path:
    return _LOG_DIR / f"output-{_today()}.log"


def _append(record: dict) -> None:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    with _log_path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _append_output(issue_number: int, agent: str, output: str, run_name: str = "") -> None:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    title = run_name or f"#{issue_number} / {agent}"
    header = f"\n{'='*60}\n[{_now()}] {title}\n{'='*60}\n"
    with _output_path().open("a", encoding="utf-8", errors="replace") as f:
        f.write(header + output + "\n")


def _print(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_issue_start(issue_number: int, title: str) -> None:
    _print(f"▶ #{issue_number} {title}")
    _append({"ts": _now(), "event": "issue_start",
             "issue_number": issue_number, "title": title})


def log_issue_done(issue_number: int) -> None:
    _print(f"✓ #{issue_number} concluída")
    _append({"ts": _now(), "event": "issue_done", "issue_number": issue_number})


def log_agent_start(issue_number: int, agent: str, step: str) -> None:
    _print(f"  → agente '{agent}' iniciado (#{issue_number})")
    _append({"ts": _now(), "event": "agent_start",
             "issue_number": issue_number, "agent": agent, "step": step})


def log_agent_end(
    issue_number: int,
    agent: str,
    step: str,
    duration_s: float,
    tokens_in: int | None,
    tokens_out: int | None,
    rework: bool,
    status: str = "ok",
    detail: str | None = None,
    output: str | None = None,
    run_name: str = "",
) -> None:
    tok = f" | tokens: {tokens_in}↑ {tokens_out}↓" if (tokens_in or tokens_out) else ""
    _print(f"  ✓ agente '{agent}' concluído em {duration_s:.1f}s{tok}")
    record = {
        "ts": _now(), "event": "agent_end",
        "issue_number": issue_number, "agent": agent, "step": step,
        "duration_s": round(duration_s, 2),
        "tokens_in": tokens_in, "tokens_out": tokens_out,
        "rework": rework, "status": status,
    }
    if detail:
        record["detail"] = detail
    _append(record)
    if output:
        _append_output(issue_number, agent, output, run_name=run_name)


def log_gate(issue_number: int, step: str, decision: str) -> None:
    icon = "✓" if decision == "approved" else "✗"
    _print(f"  {icon} gate #{issue_number}/{step}: {decision}")
    _append({"ts": _now(), "event": "gate",
             "issue_number": issue_number, "step": step, "decision": decision})


def log_sprint_end(sprint_issues: list[int]) -> None:
    _print(f"sprint encerrada — issues: {sprint_issues}")
    _append({"ts": _now(), "event": "sprint_end", "issues": sprint_issues})


def log_error(issue_number: int | None, agent: str | None, detail: str) -> None:
    ctx = f"#{issue_number} " if issue_number else ""
    _print(f"  ✗ erro {ctx}— {detail}")
    _append({"ts": _now(), "event": "error",
             "issue_number": issue_number, "agent": agent, "detail": detail})


def log_info(issue_number: int | None, agent: str | None, detail: str) -> None:
    ctx = f"#{issue_number} " if issue_number else ""
    _print(f"  ℹ {ctx}{detail}")
    _append({"ts": _now(), "event": "info",
             "issue_number": issue_number, "agent": agent, "detail": detail})


def read_all() -> list[dict]:
    """Lê todos os registros do arquivo de log do dia atual."""
    path = _log_path()
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return records
