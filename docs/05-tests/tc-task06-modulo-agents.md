Status: draft
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/04-tasks/task06-modulo-agents.md
- docs/02-architecture/cmp-agents.md

## Feature
Módulo `src/agents/` — invocação de agentes via Kiro CLI como subprocesso

## Casos de teste

### CT-043 — `run` retorna dict com `output` e `duration_s` preenchidos

**User Story:** task06 — Execução bem-sucedida de agente  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado para retornar exit code 0 e stdout `"artefato gerado"`

**Passos:**
1. Chamar `run(role="requirements", context_files=[], prompt="gere requisitos")`

**Resultado esperado:**
- Retorno é um `dict`
- `result["output"]` == `"artefato gerado"`
- `result["duration_s"]` é um `float` >= 0
- `result["tokens_in"]` é `int` ou `None`
- `result["tokens_out"]` é `int` ou `None`

---

### CT-044 — `run` retorna `tokens_in=None` e `tokens_out=None` quando Kiro CLI não os expõe

**User Story:** task06 — Tokens nullable quando não disponíveis  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado com stdout sem informação de tokens

**Passos:**
1. Chamar `run(role="requirements", context_files=[], prompt="x")`

**Resultado esperado:**
- `result["tokens_in"]` é `None`
- `result["tokens_out"]` é `None`
- Nenhuma exceção lançada

---

### CT-045 — `run` lança `TimeoutError` quando processo excede timeout

**User Story:** task06 — Controle de timeout  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado para lançar `subprocess.TimeoutExpired`

**Passos:**
1. Chamar `run(role="engineering", context_files=[], prompt="x", timeout_s=10)`

**Resultado esperado:**
- `TimeoutError` é lançado
- Mensagem menciona o agente (`"engineering"`) e o tempo limite (`10`)

---

### CT-046 — `run` lança `RuntimeError` quando código de saída é não-zero

**User Story:** task06 — Tratamento de falha do processo  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado para lançar `subprocess.CalledProcessError` com stderr preenchido

**Passos:**
1. Chamar `run(role="quality", context_files=[], prompt="x")`

**Resultado esperado:**
- `RuntimeError` é lançado
- Mensagem contém o conteúdo do stderr

---

### CT-047 — `AGENT_ROLES` contém todos os papéis válidos

**User Story:** task06 — Lista de papéis válidos  
**Tipo:** unitário  

**Pré-condição:**
- Task01 e task06 executadas

**Passos:**
1. Importar `from src.agents import AGENT_ROLES`
2. Verificar conteúdo da lista

**Resultado esperado:**
- `AGENT_ROLES` contém exatamente: `["product", "requirements", "architecture", "engineering", "quality", "operations"]`

---

### CT-048 — `run` e `AGENT_ROLES` acessíveis via `src.agents`

**User Story:** task06 — Interface pública do módulo  
**Tipo:** unitário  

**Pré-condição:**
- Task01 e task06 executadas

**Passos:**
1. Executar:
   ```python
   from src.agents import run, AGENT_ROLES
   ```

**Resultado esperado:**
- Import sem erro
- `run` é callable
- `AGENT_ROLES` é uma lista
