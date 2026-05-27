Status: draft
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/04-tasks/task05-modulo-metrics.md
- docs/02-architecture/cmp-metrics.md
- docs/02-architecture/adr-003-persistencia-estado-metricas.md

## Feature
Módulo `src/metrics/` — persistência de métricas de execução em SQLite

## Casos de teste

### CT-035 — `init_db` cria tabela `executions` idempotentemente

**User Story:** task05 — Inicialização do banco  
**Tipo:** unitário  

**Pré-condição:**
- Banco em memória (`:memory:`)

**Passos:**
1. Chamar `init_db(":memory:")` duas vezes seguidas

**Resultado esperado:**
- Nenhuma exceção em nenhuma das chamadas
- Tabela `executions` existe após as duas chamadas

---

### CT-036 — `record` insere linha com `tokens_in` e `tokens_out` nulos

**User Story:** task05 — Registro com tokens nullable (ADR-003)  
**Tipo:** unitário  

**Pré-condição:**
- Banco em memória com `init_db` já chamado

**Passos:**
1. Chamar `record(path, feature_id="f1", agent="requirements-agent", duration_s=1.5)`
2. Consultar a tabela diretamente

**Resultado esperado:**
- Uma linha inserida
- `tokens_in` é `NULL`
- `tokens_out` é `NULL`
- `duration_s` == `1.5`
- `rework` == `0`

---

### CT-037 — `record` insere linha com tokens preenchidos

**User Story:** task05 — Registro completo de execução  
**Tipo:** unitário  

**Pré-condição:**
- Banco em memória com `init_db` já chamado

**Passos:**
1. Chamar `record(path, feature_id="f1", agent="engineering-agent", duration_s=3.0, tokens_in=100, tokens_out=200, rework=True)`
2. Consultar a tabela diretamente

**Resultado esperado:**
- Uma linha inserida
- `tokens_in` == `100`
- `tokens_out` == `200`
- `rework` == `1`

---

### CT-038 — `query_by_feature` retorna apenas execuções da feature solicitada

**User Story:** task05 — Consulta por feature  
**Tipo:** unitário  

**Pré-condição:**
- Banco em memória com `init_db` já chamado
- Duas linhas inseridas: `feature_id="f1"` e `feature_id="f2"`

**Passos:**
1. Chamar `query_by_feature(path, feature_id="f1")`

**Resultado esperado:**
- Retorno é uma lista com exatamente 1 item
- O item tem `feature_id == "f1"`

---

### CT-039 — `query_totals` agrega corretamente por agente

**User Story:** task05 — Consulta de totais por agente  
**Tipo:** unitário  

**Pré-condição:**
- Banco em memória com `init_db` já chamado
- Duas linhas inseridas para `agent="requirements-agent"`: `tokens_in=10`, `tokens_out=20`, `duration_s=1.0`, `rework=False`; e `tokens_in=30`, `tokens_out=40`, `duration_s=2.0`, `rework=True`

**Passos:**
1. Chamar `query_totals(path)`

**Resultado esperado:**
- Retorno contém entrada para `"requirements-agent"`
- `total_tokens_in` == `40`
- `total_tokens_out` == `60`
- `total_duration_s` == `3.0`
- `rework_count` == `1`

---

### CT-040 — `query_by_feature` retorna lista vazia para feature inexistente

**User Story:** task05 — Consulta sem resultados  
**Tipo:** unitário  

**Pré-condição:**
- Banco em memória com `init_db` já chamado, sem registros

**Passos:**
1. Chamar `query_by_feature(path, feature_id="inexistente")`

**Resultado esperado:**
- Retorno é uma lista vazia `[]`

---

### CT-041 — Todas as funções públicas acessíveis via `src.metrics`

**User Story:** task05 — Interface pública do módulo  
**Tipo:** unitário  

**Pré-condição:**
- Task01 e task05 executadas

**Passos:**
1. Executar:
   ```python
   from src.metrics import init_db, record, query_by_feature, query_totals
   ```

**Resultado esperado:**
- Import sem erro
- Todos os símbolos são callable

---

### CT-042 — `src/metrics/store.py` não usa imports externos além de stdlib

**User Story:** task05 — Restrição de dependências  
**Tipo:** manual  

**Pré-condição:**
- Task05 executada

**Passos:**
1. Abrir `src/metrics/store.py`
2. Verificar todos os `import` e `from ... import` presentes

**Resultado esperado:**
- Apenas `sqlite3`, `pathlib` e `datetime` são importados
- Nenhum pacote de terceiros presente
