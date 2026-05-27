Status: approved
Owner: engineering-agent
Last updated: 2026-05-27T14:10-03:00

## Inputs
- docs/02-architecture/cmp-metrics.md
- docs/02-architecture/adr-003-persistencia-estado-metricas.md
- docs/04-tasks/task01-estrutura-projeto.md

## Descrição

Implementar o módulo `src/metrics/` responsável por criar e gerenciar o banco `metrics.db` (SQLite), registrar execuções de agentes e expor consultas de agregação para auditoria.

## Tipo
- dev

## Escopo técnico

- Implementar `src/metrics/store.py` com:
  - `init_db(path: str | Path = "metrics.db") -> None` — cria o banco e a tabela `executions` se não existir:
    ```sql
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
    ```
    > `tokens_in` e `tokens_out` são nullable — captura depende do Kiro CLI expor essa informação (incerteza documentada em ADR-003)
  - `record(path: str | Path, feature_id: str, agent: str, duration_s: float, tokens_in: int | None = None, tokens_out: int | None = None, rework: bool = False) -> None` — insere linha na tabela
  - `query_by_feature(path: str | Path, feature_id: str) -> list[dict]` — retorna todas as execuções de uma feature
  - `query_totals(path: str | Path) -> list[dict]` — retorna custo total por agente: `agent`, `total_tokens_in`, `total_tokens_out`, `total_duration_s`, `rework_count`
- Atualizar `src/metrics/__init__.py` para exportar `init_db`, `record`, `query_by_feature`, `query_totals`
- Criar `tests/test_metrics.py` com banco em memória (`:memory:`) cobrindo:
  - `record` insere linha corretamente com tokens nulos
  - `record` insere linha com tokens preenchidos
  - `query_by_feature` retorna apenas execuções da feature solicitada
  - `query_totals` agrega corretamente por agente

## Fora de escopo

- Dashboard ou visualização de métricas
- Exportação para formatos externos (CSV, JSON)
- Coleta automática de tokens (depende de suporte do Kiro CLI — incerteza)

## Critério de aceite (DoD)

- [ ] `init_db` cria tabela idempotentemente (sem erro se já existir)
- [ ] `tokens_in` e `tokens_out` aceitam NULL sem erro
- [ ] `record` usa escrita atômica (dentro de transaction)
- [ ] Todos os testes em `tests/test_metrics.py` passam com banco em memória
- [ ] Sem imports externos (apenas `sqlite3`, `pathlib`, `datetime` da stdlib)

## Dependências

- task01 (estrutura de projeto)

## Ordem sugerida

5 — independente dos módulos de integração; pode ser desenvolvido em paralelo com task03 e task04
