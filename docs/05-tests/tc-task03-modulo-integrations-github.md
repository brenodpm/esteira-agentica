Status: draft
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/04-tasks/task03-modulo-integrations-github.md
- docs/02-architecture/cmp-integration-github.md
- docs/02-architecture/adr-004-mecanismo-bloqueio-tasks.md
- docs/02-architecture/adr-005-interacao-humano-issues.md

## Feature
Módulo `src/integrations/github/` — abstração da API do GitHub via `gh` CLI

## Casos de teste

### CT-016 — `get_next_issue` retorna `None` quando backlog está vazio

**User Story:** task03 — Leitura do backlog  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado para retornar JSON `[]`

**Passos:**
1. Chamar `get_next_issue(config)`

**Resultado esperado:**
- Retorno é `None`

---

### CT-017 — `get_next_issue` pula issues com label `blocked`

**User Story:** task03 — Mecanismo de bloqueio (ADR-004)  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado para retornar lista com uma issue contendo label `blocked`

**Passos:**
1. Chamar `get_next_issue(config)`

**Resultado esperado:**
- Retorno é `None` (nenhuma issue elegível)

---

### CT-018 — `get_next_issue` pula issues com label `needs-human`

**User Story:** task03 — Interação humano-agente (ADR-005)  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado para retornar lista com uma issue contendo label `needs-human`

**Passos:**
1. Chamar `get_next_issue(config)`

**Resultado esperado:**
- Retorno é `None` (nenhuma issue elegível)

---

### CT-019 — `get_next_issue` retorna a issue mais antiga do backlog elegível

**User Story:** task03 — Ordenação por criação mais antiga  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado para retornar duas issues sem labels bloqueantes, com datas de criação distintas

**Passos:**
1. Chamar `get_next_issue(config)`

**Resultado esperado:**
- Retorno é a issue com data de criação mais antiga

---

### CT-020 — `get_approval_status` retorna `"approved"` quando label `approved` presente

**User Story:** task03 — Gate de aprovação  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado para retornar issue com label `approved`

**Passos:**
1. Chamar `get_approval_status(config, issue_number=1)`

**Resultado esperado:**
- Retorno é `"approved"`

---

### CT-021 — `get_approval_status` retorna `"rejected"` quando label `rejected` presente

**User Story:** task03 — Gate de aprovação  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado para retornar issue com label `rejected`

**Passos:**
1. Chamar `get_approval_status(config, issue_number=1)`

**Resultado esperado:**
- Retorno é `"rejected"`

---

### CT-022 — `get_approval_status` retorna `"pending"` quando nenhuma label de decisão presente

**User Story:** task03 — Gate de aprovação  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado para retornar issue sem labels `approved` ou `rejected`

**Passos:**
1. Chamar `get_approval_status(config, issue_number=1)`

**Resultado esperado:**
- Retorno é `"pending"`

---

### CT-023 — Erro do `gh` CLI propagado como `RuntimeError` com mensagem do stderr

**User Story:** task03 — Tratamento de erros  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado para lançar `subprocess.CalledProcessError` com stderr preenchido

**Passos:**
1. Chamar qualquer função do módulo (ex: `get_issue(config, 1)`)

**Resultado esperado:**
- `RuntimeError` é lançado
- Mensagem do `RuntimeError` contém o conteúdo do stderr

---

### CT-024 — Todas as funções públicas acessíveis via `src.integrations.github`

**User Story:** task03 — Interface pública do módulo  
**Tipo:** unitário  

**Pré-condição:**
- Task01 e task03 executadas

**Passos:**
1. Executar:
   ```python
   from src.integrations.github import (
       get_next_issue, get_issue, post_comment,
       add_label, remove_label, move_card,
       open_pr, create_issue, get_approval_status
   )
   ```

**Resultado esperado:**
- Import sem erro
- Todos os símbolos são callable

---

### CT-025 — `get_next_issue` retorna issue quando backlog tem issue elegível entre bloqueadas

**User Story:** task03 — Filtragem correta do backlog  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado para retornar lista com: uma issue com label `blocked`, uma issue sem labels bloqueantes

**Passos:**
1. Chamar `get_next_issue(config)`

**Resultado esperado:**
- Retorno é a issue sem labels bloqueantes
