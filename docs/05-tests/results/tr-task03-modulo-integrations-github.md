Status: approved
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/05-tests/tc-task03-modulo-integrations-github.md
- docs/04-tasks/task03-modulo-integrations-github.md

## Feature
Módulo `src/integrations/github/` — abstração da API do GitHub via `gh` CLI

## Execução

### CT-016 — `get_next_issue` retorna `None` quando backlog está vazio
**Resultado:** passed

### CT-017 — `get_next_issue` pula issues com label `blocked`
**Resultado:** passed

### CT-018 — `get_next_issue` pula issues com label `needs-human`
**Resultado:** passed

### CT-019 — `get_next_issue` retorna a issue mais antiga do backlog elegível
**Resultado:** passed

### CT-020 — `get_approval_status` retorna `"approved"` quando label `approved` presente
**Resultado:** passed

### CT-021 — `get_approval_status` retorna `"rejected"` quando label `rejected` presente
**Resultado:** passed

### CT-022 — `get_approval_status` retorna `"pending"` quando nenhuma label de decisão presente
**Resultado:** passed

### CT-023 — Erro do `gh` CLI propagado como `RuntimeError` com mensagem do stderr
**Resultado:** passed

### CT-024 — Todas as funções públicas acessíveis via `src.integrations.github`
**Resultado:** passed

### CT-025 — `get_next_issue` retorna issue quando backlog tem issue elegível entre bloqueadas
**Resultado:** passed

---

## Resumo

- Total: 10
- Passou: 10
- Falhou: 0
