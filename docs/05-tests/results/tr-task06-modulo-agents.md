Status: approved
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/05-tests/tc-task06-modulo-agents.md
- docs/04-tasks/task06-modulo-agents.md

## Feature
Módulo `src/agents/` — invocação de agentes via Kiro CLI como subprocesso

## Execução

### CT-043 — `run` retorna dict com `output` e `duration_s` preenchidos
**Resultado:** passed

### CT-044 — `run` retorna `tokens_in=None` e `tokens_out=None` quando Kiro CLI não os expõe
**Resultado:** passed

### CT-045 — `run` lança `TimeoutError` quando processo excede timeout
**Resultado:** passed

### CT-046 — `run` lança `RuntimeError` quando código de saída é não-zero
**Resultado:** passed

### CT-047 — `AGENT_ROLES` contém todos os papéis válidos
**Resultado:** passed

### CT-048 — `run` e `AGENT_ROLES` acessíveis via `src.agents`
**Resultado:** passed

---

## Resumo

- Total: 6
- Passou: 6
- Falhou: 0
