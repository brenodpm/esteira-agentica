Status: draft
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/04-tasks/task07-modulo-orchestrator.md
- docs/02-architecture/cmp-orchestrator.md
- docs/02-architecture/adr-002-mecanismo-orquestracao.md
- docs/02-architecture/adr-003-persistencia-estado-metricas.md

## Feature
Módulo `src/orchestrator/` — loop principal de orquestração

## Casos de teste

### CT-049 — `state.load` retorna estado inicial quando `state.json` não existe

**User Story:** task07 — Retomada de estado  
**Tipo:** unitário  

**Pré-condição:**
- Caminho de arquivo inexistente passado como argumento

**Passos:**
1. Chamar `state.load("/tmp/nao_existe.json")`

**Resultado esperado:**
- Retorno é `{"current_feature": None, "current_step": None, "status": "idle", "issue_number": None}`

---

### CT-050 — `state.load` retorna conteúdo do arquivo quando `state.json` existe

**User Story:** task07 — Retomada de estado  
**Tipo:** unitário  

**Pré-condição:**
- Arquivo temporário com conteúdo `{"current_feature": "f1", "current_step": "requirements", "status": "running", "issue_number": 42}`

**Passos:**
1. Chamar `state.load(<path_temporário>)`

**Resultado esperado:**
- Retorno é exatamente o dict persistido no arquivo

---

### CT-051 — `state.save` usa escrita atômica (arquivo temporário + `os.replace`)

**User Story:** task07 — Escrita atômica sem corrupção em crash (ADR-003)  
**Tipo:** unitário  

**Pré-condição:**
- `os.replace` mockado ou monitorado via spy

**Passos:**
1. Chamar `state.save({"status": "idle"}, path="/tmp/state_test.json")`
2. Verificar sequência de operações de I/O

**Resultado esperado:**
- Escrita ocorre em arquivo temporário (diferente do path final)
- `os.replace` é chamado para mover o temporário para o path final
- Arquivo final contém o JSON correto

---

### CT-052 — `run_once` retorna sem erro e sem alterar estado quando backlog está vazio

**User Story:** task07 — Backlog vazio  
**Tipo:** unitário  

**Pré-condição:**
- `github.get_next_issue` mockado para retornar `None`
- `state.load` mockado para retornar estado `"idle"`
- `state.save` mockado/espionado

**Passos:**
1. Chamar `run_once(config)`

**Resultado esperado:**
- Nenhuma exceção lançada
- `state.save` não é chamado (estado não alterado)
- `agents.run` não é chamado

---

### CT-053 — `run_once` avança `current_step` após execução bem-sucedida do agente

**User Story:** task07 — Progressão da sequência de agentes  
**Tipo:** unitário  

**Pré-condição:**
- `github.get_next_issue` mockado para retornar issue `{"number": 1, "title": "feat"}`
- `git.create_branch` mockado
- `agents.run` mockado para retornar `{"output": "ok", "duration_s": 1.0, "tokens_in": None, "tokens_out": None}`
- `metrics.record` mockado
- `github.move_card` mockado
- Estado inicial: `{"current_feature": None, "current_step": None, "status": "idle", "issue_number": None}`
- `config.agents_sequence = ["requirements", "architecture"]`

**Passos:**
1. Chamar `run_once(config)`
2. Capturar argumento passado para `state.save`

**Resultado esperado:**
- `state.save` chamado com `current_step` igual ao primeiro agente da sequência (`"requirements"`)
- `agents.run` chamado com `role="requirements"`

---

### CT-054 — `run_once` cria branch apenas no início de uma nova feature

**User Story:** task07 — Criação de branch no início da feature  
**Tipo:** unitário  

**Pré-condição:**
- Estado inicial com `current_step = None` (início de feature)
- Demais dependências mockadas

**Passos:**
1. Chamar `run_once(config)`

**Resultado esperado:**
- `git.create_branch` é chamado exatamente uma vez

---

### CT-055 — `run_once` não cria branch quando `current_step` já está definido (retomada)

**User Story:** task07 — Retomada sem recriar branch  
**Tipo:** unitário  

**Pré-condição:**
- Estado inicial com `current_step = "requirements"` (feature em andamento)
- `github.get_next_issue` mockado para retornar issue
- Demais dependências mockadas

**Passos:**
1. Chamar `run_once(config)`

**Resultado esperado:**
- `git.create_branch` **não** é chamado

---

### CT-056 — `run_loop` encerra sem stack trace ao receber `KeyboardInterrupt`

**User Story:** task07 — Saída limpa do loop  
**Tipo:** unitário  

**Pré-condição:**
- `run_once` mockado para lançar `KeyboardInterrupt` na primeira chamada

**Passos:**
1. Chamar `run_loop(config, poll_interval_s=0)`

**Resultado esperado:**
- Nenhuma exceção propagada para o chamador
- Processo encerra normalmente (sem traceback)

---

### CT-057 — `run_once` registra execução em `metrics.record` após agente concluir

**User Story:** task07 — Registro de métricas por execução  
**Tipo:** unitário  

**Pré-condição:**
- `agents.run` mockado para retornar `{"output": "ok", "duration_s": 2.5, "tokens_in": 10, "tokens_out": 20}`
- `metrics.record` mockado/espionado
- Demais dependências mockadas

**Passos:**
1. Chamar `run_once(config)`
2. Inspecionar chamada ao `metrics.record`

**Resultado esperado:**
- `metrics.record` chamado com `duration_s=2.5`, `tokens_in=10`, `tokens_out=20`
