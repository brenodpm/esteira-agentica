Status: approved
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/05-tests/tc-task10-prioridade-execucao.md
- docs/04-tasks/task10-prioridade-execucao.md

## Feature
Prioridade de execução de issues no orquestrador

## Execução

### CT-075 — Sub-issue `in-progress` tem prioridade sobre sub-issue no backlog
**Resultado:** passed

### CT-076 — Sub-issue `in-progress` tem prioridade sobre issue do milestone sem sub-issues
**Resultado:** passed

### CT-077 — Sub-issue no backlog tem prioridade sobre issue do milestone sem sub-issues
**Resultado:** passed

### CT-078 — Issue do milestone corrente tem prioridade sobre issue de milestone futuro
**Resultado:** passed

### CT-079 — Novo milestone só é iniciado quando milestone corrente não tem issues abertas
**Resultado:** passed

### CT-080 — Issues com label `blocked` são ignoradas em todos os níveis
**Resultado:** passed

### CT-081 — Issues com label `needs-human` são ignoradas em todos os níveis
**Resultado:** passed

### CT-082 — Empate no mesmo nível: retorna a issue mais antiga (`created_at` ascendente)
**Resultado:** passed

### CT-083 — `select_next` retorna `None` quando não há nenhuma issue disponível
**Resultado:** passed

### CT-084 — `get_current_milestone` retorna milestone do estado quando presente
**Resultado:** passed

### CT-085 — `get_current_milestone` retorna primeiro milestone com issues abertas quando estado não define milestone
**Resultado:** passed

### CT-086 — `run_once` usa `priority.select_next` em vez de `github.get_next_issue`
**Resultado:** passed

---

## Resumo

- Total: 12
- Passou: 12
- Falhou: 0
