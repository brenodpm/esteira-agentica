import pytest
from src.metrics import init_db, record, query_by_feature, query_totals
from src.metrics.store import _connect


MEM = ":memory:"


@pytest.fixture
def db(tmp_path):
    """Shared in-memory DB via file path so all calls share the same connection."""
    p = tmp_path / "test.db"
    init_db(p)
    return p


# CT-035 — init_db cria tabela idempotentemente
def test_init_db_idempotent():
    import sqlite3
    conn = sqlite3.connect(MEM)
    conn.row_factory = sqlite3.Row
    # Simulate two calls on same connection by calling DDL twice
    from src.metrics.store import _DDL
    conn.execute(_DDL)
    conn.execute(_DDL)  # must not raise
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='executions'").fetchone()
    assert row is not None


# CT-036 — record insere linha com tokens nulos
def test_record_null_tokens(db):
    record(db, feature_id="f1", agent="requirements-agent", duration_s=1.5)
    with _connect(db) as conn:
        row = conn.execute("SELECT * FROM executions").fetchone()
    assert row["tokens_in"] is None
    assert row["tokens_out"] is None
    assert row["duration_s"] == 1.5
    assert row["rework"] == 0


# CT-037 — record insere linha com tokens preenchidos
def test_record_with_tokens(db):
    record(db, feature_id="f1", agent="engineering-agent", duration_s=3.0,
           tokens_in=100, tokens_out=200, rework=True)
    with _connect(db) as conn:
        row = conn.execute("SELECT * FROM executions").fetchone()
    assert row["tokens_in"] == 100
    assert row["tokens_out"] == 200
    assert row["rework"] == 1


# CT-038 — query_by_feature retorna apenas execuções da feature solicitada
def test_query_by_feature_filters(db):
    record(db, feature_id="f1", agent="a", duration_s=1.0)
    record(db, feature_id="f2", agent="a", duration_s=1.0)
    result = query_by_feature(db, feature_id="f1")
    assert len(result) == 1
    assert result[0]["feature_id"] == "f1"


# CT-039 — query_totals agrega corretamente por agente
def test_query_totals_aggregation(db):
    record(db, feature_id="f1", agent="requirements-agent", duration_s=1.0,
           tokens_in=10, tokens_out=20, rework=False)
    record(db, feature_id="f1", agent="requirements-agent", duration_s=2.0,
           tokens_in=30, tokens_out=40, rework=True)
    totals = query_totals(db)
    row = next(r for r in totals if r["agent"] == "requirements-agent")
    assert row["total_tokens_in"] == 40
    assert row["total_tokens_out"] == 60
    assert row["total_duration_s"] == pytest.approx(3.0)
    assert row["rework_count"] == 1


# CT-040 — query_by_feature retorna lista vazia para feature inexistente
def test_query_by_feature_empty(db):
    assert query_by_feature(db, feature_id="inexistente") == []


# CT-041 — todas as funções públicas acessíveis via src.metrics
def test_public_interface():
    from src.metrics import init_db, record, query_by_feature, query_totals
    assert all(callable(f) for f in [init_db, record, query_by_feature, query_totals])


# CT-042 — store.py não usa imports externos além de stdlib
def test_no_external_imports():
    import ast, pathlib
    source = pathlib.Path("src/metrics/store.py").read_text()
    tree = ast.parse(source)
    allowed = {"sqlite3", "pathlib", "datetime"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in allowed, f"Unexpected import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            assert node.module.split(".")[0] in allowed, f"Unexpected import: {node.module}"
