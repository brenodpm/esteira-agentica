Status: draft
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/04-tasks/task01-estrutura-projeto.md
- docs/01-requirements/meeting-01.md

## Feature
Estrutura base do projeto Python

## Casos de teste

### CT-001 — Estrutura de diretórios corresponde ao definido em meeting-01.md

**User Story:** task01 — Criar estrutura de diretórios e arquivos base  
**Tipo:** manual  

**Pré-condição:**
- Task01 executada

**Passos:**
1. Listar recursivamente o conteúdo de `src/`

**Resultado esperado:**
- Existem os diretórios: `src/orchestrator/`, `src/agents/`, `src/integrations/`, `src/integrations/github/`, `src/integrations/git/`, `src/metrics/`, `src/config/`
- Cada diretório contém `__init__.py`
- `src/__main__.py` existe

---

### CT-002 — `python -m src` executa sem erro e imprime versão

**User Story:** task01 — Entry point mínimo  
**Tipo:** manual  

**Pré-condição:**
- Python >= 3.11 disponível no ambiente
- Task01 executada

**Passos:**
1. Na raiz do projeto, executar `python -m src`

**Resultado esperado:**
- Exit code 0
- Saída contém a versão do projeto (ex: `0.1.0`)
- Nenhuma exceção ou traceback exibido

---

### CT-003 — `pyproject.toml` é válido e contém campos obrigatórios

**User Story:** task01 — Metadados do projeto  
**Tipo:** manual  

**Pré-condição:**
- Task01 executada

**Passos:**
1. Executar `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"`
2. Verificar presença dos campos `[project].name`, `[project].version`, `[project].requires-python`

**Resultado esperado:**
- Nenhuma exceção (TOML válido)
- `name` presente e não vazio
- `version` igual a `"0.1.0"`
- `requires-python` igual a `">=3.11"`

---

### CT-004 — `config/project.json` é JSON válido com todos os campos padrão

**User Story:** task01 — Configuração padrão do projeto  
**Tipo:** manual  

**Pré-condição:**
- Task01 executada

**Passos:**
1. Executar `python -c "import json; d=json.load(open('config/project.json')); print(list(d.keys()))"`
2. Verificar presença das chaves: `repo`, `gitflow`, `board`, `agents_sequence`
3. Verificar que `gitflow` contém `branch_base` e `prefixes`
4. Verificar que `board` contém `columns` e `labels`

**Resultado esperado:**
- Nenhuma exceção (JSON válido)
- Todas as chaves de primeiro nível presentes: `repo`, `gitflow`, `board`, `agents_sequence`
- `gitflow.branch_base` presente
- `gitflow.prefixes` presente
- `board.columns` presente
- `board.labels` presente

---

### CT-005 — `state.json` existe com estrutura inicial correta

**User Story:** task01 — Estado inicial da orquestração  
**Tipo:** manual  

**Pré-condição:**
- Task01 executada

**Passos:**
1. Executar `python -c "import json; print(json.load(open('state.json')))"`

**Resultado esperado:**
- Nenhuma exceção (JSON válido)
- Conteúdo exato: `{"current_feature": null, "current_step": null, "status": "idle"}`

---

### CT-006 — `.gitignore` cobre entradas obrigatórias

**User Story:** task01 — Controle de versionamento  
**Tipo:** manual  

**Pré-condição:**
- Task01 executada

**Passos:**
1. Abrir `.gitignore` e verificar presença das entradas

**Resultado esperado:**
- `.gitignore` contém `__pycache__`
- `.gitignore` contém `*.pyc`
- `.gitignore` contém `metrics.db`
- `.gitignore` contém `.env`
