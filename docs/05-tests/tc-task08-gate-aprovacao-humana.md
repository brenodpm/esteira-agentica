Status: draft
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/04-tasks/task08-gate-aprovacao-humana.md
- docs/02-architecture/adr-002-mecanismo-orquestracao.md
- docs/02-architecture/adr-005-interacao-humano-issues.md

## Feature
Gate de aprovação humana no orquestrador

## Casos de teste

### CT-058 — `run_once` com `status="awaiting_approval"` e aprovação `"pending"` não altera estado

**User Story:** task08 — Aguardar aprovação sem avançar  
**Tipo:** unitário  

**Pré-condição:**
- Estado: `{"status": "awaiting_approval", "current_step": "requirements", "issue_number": 1, "rework": False}`
- `github.get_approval_status` mockado para retornar `"pending"`
- `state.save` espionado

**Passos:**
1. Chamar `run_once(config)`

**Resultado esperado:**
- `state.save` não é chamado
- `agents.run` não é chamado

---

### CT-059 — `run_once` com `status="awaiting_approval"` e aprovação `"approved"` avança `current_step`

**User Story:** task08 — Progressão após aprovação humana  
**Tipo:** unitário  

**Pré-condição:**
- Estado: `{"status": "awaiting_approval", "current_step": "requirements", "issue_number": 1, "rework": False}`
- `github.get_approval_status` mockado para retornar `"approved"`
- `github.remove_label` mockado
- `state.save` espionado

**Passos:**
1. Chamar `run_once(config)`
2. Capturar argumento passado para `state.save`

**Resultado esperado:**
- `state.save` chamado com `status == "idle"`
- `current_step` avançado para o próximo agente da sequência
- `github.remove_label` chamado com label `"approved"`

---

### CT-060 — `run_once` com `status="awaiting_approval"` e aprovação `"rejected"` mantém `current_step` e seta `rework=True`

**User Story:** task08 — Retrabalho após rejeição  
**Tipo:** unitário  

**Pré-condição:**
- Estado: `{"status": "awaiting_approval", "current_step": "requirements", "issue_number": 1, "rework": False}`
- `github.get_approval_status` mockado para retornar `"rejected"`
- `github.remove_label` mockado
- `state.save` espionado

**Passos:**
1. Chamar `run_once(config)`
2. Capturar argumento passado para `state.save`

**Resultado esperado:**
- `state.save` chamado com `current_step == "requirements"` (inalterado)
- `state.save` chamado com `rework == True`
- `github.remove_label` chamado com label `"rejected"`

---

### CT-061 — Re-execução com `rework=True` chama `metrics.record` com `rework=True`

**User Story:** task08 — Registro de retrabalho em métricas  
**Tipo:** unitário  

**Pré-condição:**
- Estado: `{"status": "idle", "current_step": "requirements", "issue_number": 1, "rework": True}`
- `agents.run` mockado para retornar resultado válido
- `metrics.record` espionado
- Demais dependências mockadas

**Passos:**
1. Chamar `run_once(config)`
2. Inspecionar chamada ao `metrics.record`

**Resultado esperado:**
- `metrics.record` chamado com `rework=True`

---

### CT-062 — Após execução do agente, output é postado como comentário na issue

**User Story:** task08 — Comunicação do resultado via GitHub  
**Tipo:** unitário  

**Pré-condição:**
- Estado: `{"status": "idle", "current_step": None, "issue_number": 1, "rework": False}`
- `agents.run` mockado para retornar `{"output": "artefato gerado", "duration_s": 1.0, "tokens_in": None, "tokens_out": None}`
- `github.post_comment` espionado
- Demais dependências mockadas

**Passos:**
1. Chamar `run_once(config)`
2. Inspecionar chamada ao `github.post_comment`

**Resultado esperado:**
- `github.post_comment` chamado com `body` contendo `"artefato gerado"`

---

### CT-063 — Após execução do agente, estado é salvo com `status="awaiting_approval"`

**User Story:** task08 — Persistência do estado de espera entre reinicializações  
**Tipo:** unitário  

**Pré-condição:**
- Estado: `{"status": "idle", "current_step": None, "issue_number": 1, "rework": False}`
- `agents.run` mockado para retornar resultado válido
- `state.save` espionado
- Demais dependências mockadas

**Passos:**
1. Chamar `run_once(config)`
2. Capturar último argumento passado para `state.save`

**Resultado esperado:**
- `state.save` chamado com `status == "awaiting_approval"`
- `current_step` mantido (não avançado ainda)

---

### CT-064 — Estado `"awaiting_approval"` persiste após reinicialização do processo

**User Story:** task08 — Durabilidade do estado de aprovação  
**Tipo:** unitário  

**Pré-condição:**
- `state.json` em disco com `{"status": "awaiting_approval", "current_step": "requirements", "issue_number": 1, "rework": False}`

**Passos:**
1. Chamar `state.load(<path>)`

**Resultado esperado:**
- `result["status"]` == `"awaiting_approval"`
- `result["current_step"]` == `"requirements"`
- `result["rework"]` == `False`
