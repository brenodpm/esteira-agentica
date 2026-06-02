Status: draft
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/04-tasks/task09-mecanismo-bloqueio.md
- docs/02-architecture/adr-004-mecanismo-bloqueio-tasks.md
- docs/02-architecture/adr-005-interacao-humano-issues.md

## Feature
Mecanismo de bloqueio de tasks no orquestrador

## Casos de teste

### CT-065 — `create_blocker` cria issue bloqueante e adiciona label `blocked` na issue corrente

**User Story:** task09 — Criação de bloqueio por dependência  
**Tipo:** unitário  

**Pré-condição:**
- `github.create_issue` mockado para retornar `42`
- `github.add_label` espionado
- `config` com repositório válido

**Passos:**
1. Chamar `create_blocker(config, blocked_issue=10, title="Depende de X", body="Descrição do bloqueio")`
2. Capturar chamadas a `github.create_issue` e `github.add_label`

**Resultado esperado:**
- `github.create_issue` chamado com `title="Depende de X"` e `body="Descrição do bloqueio"`
- `github.add_label` chamado com `issue_number=10` e `label="blocked"`
- Retorno da função é `42` (número da issue criada)

---

### CT-066 — `create_blocker` com `needs_human=True` adiciona label `needs-human` na issue criada

**User Story:** task09 — Bloqueio por intervenção humana  
**Tipo:** unitário  

**Pré-condição:**
- `github.create_issue` mockado para retornar `43`
- `github.add_label` espionado
- `config` com repositório válido

**Passos:**
1. Chamar `create_blocker(config, blocked_issue=11, title="Pergunta ao humano", body="...", needs_human=True)`
2. Capturar todas as chamadas a `github.add_label`

**Resultado esperado:**
- `github.add_label` chamado com `issue_number=43` e `label="needs-human"`
- `github.add_label` chamado com `issue_number=11` e `label="blocked"`

---

### CT-067 — `create_blocker` com `needs_human=False` não adiciona label `needs-human`

**User Story:** task09 — Bloqueio de agente não escala para humano  
**Tipo:** unitário  

**Pré-condição:**
- `github.create_issue` mockado para retornar `44`
- `github.add_label` espionado

**Passos:**
1. Chamar `create_blocker(config, blocked_issue=12, title="Bloqueio técnico", body="...", needs_human=False)`
2. Inspecionar todas as chamadas a `github.add_label`

**Resultado esperado:**
- Nenhuma chamada a `github.add_label` com `label="needs-human"`

---

### CT-068 — `unblock_dependents` remove label `blocked` de issues que referenciam a issue resolvida

**User Story:** task09 — Desbloqueio automático após conclusão  
**Tipo:** unitário  

**Pré-condição:**
- `github.get_issues_with_label` mockado para retornar issues `[20, 21]` com label `blocked` que referenciam issue `#5` no corpo
- `github.remove_label` espionado
- `github.move_card` espionado

**Passos:**
1. Chamar `unblock_dependents(config, resolved_issue=5)`
2. Capturar chamadas a `github.remove_label` e `github.move_card`

**Resultado esperado:**
- `github.remove_label` chamado com `issue_number=20` e `label="blocked"`
- `github.remove_label` chamado com `issue_number=21` e `label="blocked"`
- `github.move_card` chamado para issues `20` e `21` com destino `"Backlog"`
- Retorno da função é `[20, 21]`

---

### CT-069 — `unblock_dependents` retorna lista vazia quando nenhuma issue referencia a issue resolvida

**User Story:** task09 — Desbloqueio sem dependentes  
**Tipo:** unitário  

**Pré-condição:**
- `github.get_issues_with_label` mockado para retornar lista vazia
- `github.remove_label` espionado

**Passos:**
1. Chamar `unblock_dependents(config, resolved_issue=99)`

**Resultado esperado:**
- `github.remove_label` não é chamado
- Retorno da função é `[]`

---

### CT-070 — `detect_deadlock` retorna `True` quando todas as issues disponíveis têm label `blocked`

**User Story:** task09 — Detecção de ciclo de bloqueio mútuo  
**Tipo:** unitário  

**Pré-condição:**
- `github.get_next_issue` mockado para retornar `None` (nenhuma issue sem `blocked`)
- `github.get_issues_with_label` mockado para retornar issues `[30, 31]` com label `blocked`

**Passos:**
1. Chamar `detect_deadlock(config)`

**Resultado esperado:**
- Retorno é `True`

---

### CT-071 — `detect_deadlock` retorna `False` quando há pelo menos uma issue sem label `blocked`

**User Story:** task09 — Ausência de deadlock com issue disponível  
**Tipo:** unitário  

**Pré-condição:**
- `github.get_next_issue` mockado para retornar issue `32` (sem label `blocked`)

**Passos:**
1. Chamar `detect_deadlock(config)`

**Resultado esperado:**
- Retorno é `False`

---

### CT-072 — `run_once` exclui issues com label `blocked` ao selecionar próxima issue

**User Story:** task09 — Orquestrador pula issues bloqueadas  
**Tipo:** unitário  

**Pré-condição:**
- `github.get_next_issue` mockado para retornar `None` (simula que todas as issues disponíveis estão bloqueadas ou não há issues)
- `state.save` espionado

**Passos:**
1. Chamar `run_once(config)` com estado `{"status": "idle", "issue_number": None}`
2. Verificar que `github.get_next_issue` é chamado sem incluir issues com label `blocked`

**Resultado esperado:**
- `github.get_next_issue` chamado com parâmetro que exclui label `blocked`
- `agents.run` não é chamado

---

### CT-073 — `run_once` chama `_unblock_dependents` após conclusão de issue

**User Story:** task09 — Desbloqueio automático integrado ao loop principal  
**Tipo:** unitário  

**Pré-condição:**
- Estado: `{"status": "idle", "current_step": None, "issue_number": 5, "rework": False}`
- `agents.run` mockado para retornar resultado válido
- `github.get_approval_status` mockado para retornar `"approved"` (simula conclusão)
- `blocker.unblock_dependents` espionado

**Passos:**
1. Chamar `run_once(config)` até issue ser concluída
2. Verificar chamada a `blocker.unblock_dependents`

**Resultado esperado:**
- `blocker.unblock_dependents` chamado com `resolved_issue=5`

---

### CT-074 — Deadlock detectado cria issue `needs-human` e para o loop

**User Story:** task09 — Escalada de ciclo de bloqueio mútuo  
**Tipo:** unitário  

**Pré-condição:**
- `blocker.detect_deadlock` mockado para retornar `True`
- `github.create_issue` espionado
- `github.add_label` espionado
- Loop do orquestrador em execução

**Passos:**
1. Chamar `run_once(config)` com estado `{"status": "idle", "issue_number": None}`
2. Capturar chamadas a `github.create_issue` e `github.add_label`

**Resultado esperado:**
- `github.create_issue` chamado com body descrevendo o ciclo de bloqueio
- `github.add_label` chamado com `label="needs-human"` na issue criada
- Loop encerrado (sem nova chamada a `agents.run`)
