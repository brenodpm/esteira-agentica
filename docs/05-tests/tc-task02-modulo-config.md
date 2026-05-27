Status: draft
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/04-tasks/task02-modulo-config.md
- docs/02-architecture/cmp-config.md

## Feature
Módulo `src/config/` — carregamento e validação de configuração

## Casos de teste

### CT-007 — `load()` retorna dict com todos os campos para JSON completo

**User Story:** task02 — Carregar JSON válido completo  
**Tipo:** unitário  

**Pré-condição:**
- `config/project.json` existe com todos os campos: `repo`, `gitflow`, `board`, `agents_sequence`

**Passos:**
1. Chamar `from src.config import load; cfg = load("config/project.json")`

**Resultado esperado:**
- Retorno é um `dict`
- `cfg["repo"]` presente e não vazio
- `cfg["gitflow"]["branch_base"]` presente
- `cfg["gitflow"]["prefixes"]` presente
- `cfg["board"]["columns"]` presente
- `cfg["board"]["labels"]` presente
- `cfg["agents_sequence"]` presente

---

### CT-008 — `load()` aplica default `gitflow.branch_base` quando ausente

**User Story:** task02 — Aplicar defaults para campos opcionais ausentes  
**Tipo:** unitário  

**Pré-condição:**
- JSON de entrada contém `repo` mas não contém `gitflow.branch_base`

**Passos:**
1. Criar arquivo JSON temporário com `{"repo": "owner/repo"}`
2. Chamar `load(<path_temporário>)`

**Resultado esperado:**
- `cfg["gitflow"]["branch_base"]` == `"develop"`

---

### CT-009 — `load()` aplica default `gitflow.prefixes` quando ausente

**User Story:** task02 — Aplicar defaults para campos opcionais ausentes  
**Tipo:** unitário  

**Pré-condição:**
- JSON de entrada contém `repo` mas não contém `gitflow.prefixes`

**Passos:**
1. Criar arquivo JSON temporário com `{"repo": "owner/repo"}`
2. Chamar `load(<path_temporário>)`

**Resultado esperado:**
- `cfg["gitflow"]["prefixes"]["feature"]` == `"feature/"`
- `cfg["gitflow"]["prefixes"]["fix"]` == `"fix/"`
- `cfg["gitflow"]["prefixes"]["release"]` == `"release/"`
- `cfg["gitflow"]["prefixes"]["hotfix"]` == `"hotfix/"`

---

### CT-010 — `load()` aplica default `board.columns` quando ausente

**User Story:** task02 — Aplicar defaults para campos opcionais ausentes  
**Tipo:** unitário  

**Pré-condição:**
- JSON de entrada contém `repo` mas não contém `board.columns`

**Passos:**
1. Criar arquivo JSON temporário com `{"repo": "owner/repo"}`
2. Chamar `load(<path_temporário>)`

**Resultado esperado:**
- `cfg["board"]["columns"]` == `["Backlog", "In Progress", "Done"]`

---

### CT-011 — `load()` aplica default `board.labels` quando ausente

**User Story:** task02 — Aplicar defaults para campos opcionais ausentes  
**Tipo:** unitário  

**Pré-condição:**
- JSON de entrada contém `repo` mas não contém `board.labels`

**Passos:**
1. Criar arquivo JSON temporário com `{"repo": "owner/repo"}`
2. Chamar `load(<path_temporário>)`

**Resultado esperado:**
- `cfg["board"]["labels"]` == `{}`

---

### CT-012 — `load()` aplica default `agents_sequence` quando ausente

**User Story:** task02 — Aplicar defaults para campos opcionais ausentes  
**Tipo:** unitário  

**Pré-condição:**
- JSON de entrada contém `repo` mas não contém `agents_sequence`

**Passos:**
1. Criar arquivo JSON temporário com `{"repo": "owner/repo"}`
2. Chamar `load(<path_temporário>)`

**Resultado esperado:**
- `cfg["agents_sequence"]` é uma lista não vazia

---

### CT-013 — `load()` lança `ValueError` quando `repo` está ausente

**User Story:** task02 — Validar campo obrigatório  
**Tipo:** unitário  

**Pré-condição:**
- JSON de entrada não contém o campo `repo`

**Passos:**
1. Criar arquivo JSON temporário com `{}`
2. Chamar `load(<path_temporário>)` dentro de bloco `try/except ValueError`

**Resultado esperado:**
- `ValueError` é lançado
- Mensagem de erro é clara e menciona `repo`

---

### CT-014 — `load` está acessível via `src.config`

**User Story:** task02 — Interface pública do módulo  
**Tipo:** unitário  

**Pré-condição:**
- Task01 e task02 executadas

**Passos:**
1. Executar `from src.config import load`

**Resultado esperado:**
- Import sem erro
- `load` é callable

---

### CT-015 — `load()` não usa imports externos além de `json` e `pathlib`

**User Story:** task02 — Restrição de dependências  
**Tipo:** manual  

**Pré-condição:**
- Task02 executada

**Passos:**
1. Abrir `src/config/loader.py`
2. Verificar todos os `import` e `from ... import` presentes

**Resultado esperado:**
- Apenas `json` e `pathlib` são importados (stdlib)
- Nenhum pacote de terceiros presente
