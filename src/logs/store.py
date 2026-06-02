"""Log estruturado de execução da esteira em formato JSONL.

Cada linha é um JSON com os campos:
  ts, event, issue_number, agent, step, duration_s, tokens_in, tokens_out,
  rework, status, detail (opcional)

O arquivo é append-only — nunca sobrescrito.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path("logs/esteira.jsonl")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append(record: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def log_agent_start(issue_number: int, agent: str, step: str) -> None:
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
) -> None:
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


def log_gate(issue_number: int, step: str, decision: str) -> None:
    _append({"ts": _now(), "event": "gate",
             "issue_number": issue_number, "step": step, "decision": decision})


def log_issue_start(issue_number: int, title: str) -> None:
    _append({"ts": _now(), "event": "issue_start",
             "issue_number": issue_number, "title": title})


def log_issue_done(issue_number: int) -> None:
    _append({"ts": _now(), "event": "issue_done", "issue_number": issue_number})


def log_sprint_end(sprint_issues: list[int]) -> None:
    _append({"ts": _now(), "event": "sprint_end", "issues": sprint_issues})


def log_error(issue_number: int | None, agent: str | None, detail: str) -> None:
    _append({"ts": _now(), "event": "error",
             "issue_number": issue_number, "agent": agent, "detail": detail})


def read_all() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    records = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return records
