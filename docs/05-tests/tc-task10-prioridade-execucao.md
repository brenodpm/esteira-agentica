Status: draft
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/04-tasks/task10-prioridade-execucao.md
- docs/02-architecture/adr-006-prioridade-execucao-tasks.md

## Feature
Prioridade de execução de issues no orquestrador

## Casos de teste

### CT-075 — Sub-issue `in-progress` tem prioridade sobre sub-issue no backlog

**User Story:** task10 — Hierarquia nível 1 > nível 2  
**Tipo:** unitário  

**Pré-condição:**
- Milestone corrente: `"m1"`
- Sub-issues disponíveis: `[{id: 10, labels: ["in-progress"], created_at: "2026-01-02"}, {id: 11, labels: [], created_at: "2026-01-01"}]`
- Nenhuma label `blocked` ou `needs-human`

**Passos:**
1. Chamar `select_next(config, state)`

**Resultado esperado:**
- Retorna issue `10` (in-progress, mesmo sendo mais nova)

---

### CT-076 — Sub-issue `in-progress` tem prioridade sobre issue do milestone sem sub-issues

**User Story:** task10 — Hierarquia nível 1 > nível 3  
**Tipo:** unitário  

**Pré-condição:**
- Milestone corrente: `"m1"`
- Sub-issue `in-progress`: `{id: 10, labels: ["in-progress"]}`
- Issue do milestone sem sub-issues: `{id: 20, labels: []}`

**Passos:**
1. Chamar `select_next(config, state)`

**Resultado esperado:**
- Retorna issue `10`

---

### CT-077 — Sub-issue no backlog tem prioridade sobre issue do milestone sem sub-issues

**User Story:** task10 — Hierarquia nível 2 > nível 3  
**Tipo:** unitário  

**Pré-condição:**
- Milestone corrente: `"m1"`
- Nenhuma sub-issue `in-progress`
- Sub-issue no backlog: `{id: 11, labels: [], created_at: "2026-01-02"}`
- Issue do milestone sem sub-issues: `{id: 20, labels: [], created_at: "2026-01-01"}`

**Passos:**
1. Chamar `select_next(config, state)`

**Resultado esperado:**
- Retorna issue `11` (sub-issue do backlog, mesmo sendo mais nova)

---

### CT-078 — Issue do milestone corrente tem prioridade sobre issue de milestone futuro

**User Story:** task10 — Hierarquia nível 3 > nível 4  
**Tipo:** unitário  

**Pré-condição:**
- Milestone corrente: `"m1"` com issue aberta `{id: 20, labels: []}`
- Milestone futuro: `"m2"` com issue `{id: 30, labels: []}`
- Nenhuma sub-issue pendente

**Passos:**
1. Chamar `select_next(config, state)`

**Resultado esperado:**
- Retorna issue `20` (milestone corrente)

---

### CT-079 — Novo milestone só é iniciado quando milestone corrente não tem issues abertas

**User Story:** task10 — Transição de milestone  
**Tipo:** unitário  

**Pré-condição:**
- Milestone corrente: `"m1"` sem issues abertas (todas fechadas)
- Milestone seguinte: `"m2"` com issue `{id: 30, labels: []}`

**Passos:**
1. Chamar `select_next(config, state)`

**Resultado esperado:**
- Retorna issue `30` (primeiro item do milestone `"m2"`)

---

### CT-080 — Issues com label `blocked` são ignoradas em todos os níveis

**User Story:** task10 — Filtro de bloqueio na seleção  
**Tipo:** unitário  

**Pré-condição:**
- Milestone corrente: `"m1"`
- Sub-issue `in-progress` com label `blocked`: `{id: 10, labels: ["in-progress", "blocked"]}`
- Sub-issue no backlog com label `blocked`: `{id: 11, labels: ["blocked"]}`
- Issue do milestone com label `blocked`: `{id: 20, labels: ["blocked"]}`
- Nenhuma outra issue disponível

**Passos:**
1. Chamar `select_next(config, state)`

**Resultado esperado:**
- Retorna `None`

---

### CT-081 — Issues com label `needs-human` são ignoradas em todos os níveis

**User Story:** task10 — Filtro de intervenção humana na seleção  
**Tipo:** unitário  

**Pré-condição:**
- Milestone corrente: `"m1"`
- Única issue disponível: `{id: 10, labels: ["needs-human"]}`

**Passos:**
1. Chamar `select_next(config, state)`

**Resultado esperado:**
- Retorna `None`

---

### CT-082 — Empate no mesmo nível: retorna a issue mais antiga (`created_at` ascendente)

**User Story:** task10 — Desempate por ordem de criação  
**Tipo:** unitário  

**Pré-condição:**
- Milestone corrente: `"m1"`
- Duas sub-issues no backlog sem labels de bloqueio:
  - `{id: 11, labels: [], created_at: "2026-01-03"}`
  - `{id: 12, labels: [], created_at: "2026-01-01"}`

**Passos:**
1. Chamar `select_next(config, state)`

**Resultado esperado:**
- Retorna issue `12` (mais antiga)

---

### CT-083 — `select_next` retorna `None` quando não há nenhuma issue disponível

**User Story:** task10 — Ausência de trabalho disponível  
**Tipo:** unitário  

**Pré-condição:**
- Nenhum milestone com issues abertas
- `github.get_issues` mockado para retornar `[]` em todos os níveis

**Passos:**
1. Chamar `select_next(config, state)`

**Resultado esperado:**
- Retorna `None`

---

### CT-084 — `get_current_milestone` retorna milestone do estado quando presente

**User Story:** task10 — Continuidade do milestone em execução  
**Tipo:** unitário  

**Pré-condição:**
- `state = {"current_milestone": "m2"}`

**Passos:**
1. Chamar `get_current_milestone(config, state)`

**Resultado esperado:**
- Retorna `"m2"`

---

### CT-085 — `get_current_milestone` retorna primeiro milestone com issues abertas quando estado não define milestone

**User Story:** task10 — Inicialização do milestone corrente  
**Tipo:** unitário  

**Pré-condição:**
- `state = {}` (sem `current_milestone`)
- `github.get_milestones` mockado para retornar `["m1", "m2"]`
- `github.get_issues` mockado: `"m1"` tem issues abertas, `"m2"` também

**Passos:**
1. Chamar `get_current_milestone(config, state)`

**Resultado esperado:**
- Retorna `"m1"` (primeiro com issues abertas)

---

### CT-086 — `run_once` usa `priority.select_next` em vez de `github.get_next_issue`

**User Story:** task10 — Integração da prioridade no loop principal  
**Tipo:** unitário  

**Pré-condição:**
- `priority.select_next` espionado, retorna `{id: 10, labels: []}`
- `github.get_next_issue` espionado
- Estado: `{"status": "idle", "issue_number": None}`

**Passos:**
1. Chamar `run_once(config)`
2. Verificar qual função foi chamada para seleção de issue

**Resultado esperado:**
- `priority.select_next` é chamado
- `github.get_next_issue` não é chamado diretamente para seleção
