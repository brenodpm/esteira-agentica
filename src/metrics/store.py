import sqlite3
from datetime import datetime, timezone
from pathlib import Path

_DDL = """
CREATE TABLE IF NOT EXISTS executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    tokens_in INTEGER,
    tokens_out INTEGER,
    duration_s REAL NOT NULL,
    rework INTEGER NOT NULL DEFAULT 0,
    timestamp TEXT NOT NULL
)
"""


def _connect(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path: str | Path = "metrics.db") -> None:
    with _connect(path) as conn:
        conn.execute(_DDL)


def record(
    path: str | Path,
    feature_id: str,
    agent: str,
    duration_s: float,
    tokens_in: int | None = None,
    tokens_out: int | None = None,
    rework: bool = False,
) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    with _connect(path) as conn:
        conn.execute(
            "INSERT INTO executions (feature_id, agent, tokens_in, tokens_out, duration_s, rework, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (feature_id, agent, tokens_in, tokens_out, duration_s, int(rework), ts),
        )


def query_by_feature(path: str | Path, feature_id: str) -> list[dict]:
    with _connect(path) as conn:
        rows = conn.execute(
            "SELECT * FROM executions WHERE feature_id = ?", (feature_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def query_totals(path: str | Path) -> list[dict]:
    with _connect(path) as conn:
        rows = conn.execute(
            "SELECT agent, "
            "SUM(tokens_in) AS total_tokens_in, "
            "SUM(tokens_out) AS total_tokens_out, "
            "SUM(duration_s) AS total_duration_s, "
            "SUM(rework) AS rework_count "
            "FROM executions GROUP BY agent"
        ).fetchall()
    return [dict(r) for r in rows]
