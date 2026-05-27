Status: done
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/04-tasks/task04-modulo-integrations-git.md
- docs/02-architecture/cmp-integration-git.md
- docs/gitflow.md

## Feature
Módulo `src/integrations/git/` — operações de versionamento via `git` CLI

## Casos de teste

### CT-026 — `create_branch` monta nome correto com prefixo do gitflow

**User Story:** task04 — Criação de branch com prefixo configurado  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado para não executar comandos reais
- Config com `gitflow.prefixes.feature = "feature/"`

**Passos:**
1. Chamar `create_branch(config, branch_type="feature", name="minha-feature")`

**Resultado esperado:**
- Retorno é `"feature/minha-feature"`
- `subprocess.run` chamado com argumento contendo `"feature/minha-feature"`

---

### CT-027 — `create_branch` usa `branch_base` da config como ponto de partida

**User Story:** task04 — Branch parte de `gitflow.branch_base`  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado
- Config com `gitflow.branch_base = "develop"`

**Passos:**
1. Chamar `create_branch(config, branch_type="feature", name="x")`
2. Inspecionar chamadas ao `subprocess.run`

**Resultado esperado:**
- Uma das chamadas ao `subprocess.run` contém `"develop"` como referência de origem (ex: `git checkout -b feature/x develop` ou equivalente)

---

### CT-028 — `create_branch` respeita prefixo configurado para tipo `fix`

**User Story:** task04 — Prefixos configuráveis por tipo  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado
- Config com `gitflow.prefixes.fix = "fix/"`

**Passos:**
1. Chamar `create_branch(config, branch_type="fix", name="bug-123")`

**Resultado esperado:**
- Retorno é `"fix/bug-123"`

---

### CT-029 — `commit` com `files=None` executa `git add -A`

**User Story:** task04 — Commit de todos os arquivos modificados  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado

**Passos:**
1. Chamar `commit(config, message="feat: inicial", files=None)`
2. Inspecionar chamadas ao `subprocess.run`

**Resultado esperado:**
- Uma das chamadas contém `["git", "add", "-A"]` (ou equivalente)
- Uma das chamadas contém `["git", "commit", "-m", "feat: inicial"]` (ou equivalente)

---

### CT-030 — `commit` com lista de arquivos executa `git add` apenas nos arquivos listados

**User Story:** task04 — Commit seletivo de arquivos  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado

**Passos:**
1. Chamar `commit(config, message="fix: ajuste", files=["src/foo.py", "src/bar.py"])`
2. Inspecionar chamadas ao `subprocess.run`

**Resultado esperado:**
- Chamada ao `git add` inclui `"src/foo.py"` e `"src/bar.py"`
- Chamada ao `git add` **não** usa `-A`

---

### CT-031 — `push` executa `git push -u origin <branch>`

**User Story:** task04 — Push da branch para o remote  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado

**Passos:**
1. Chamar `push("feature/minha-feature")`
2. Inspecionar chamadas ao `subprocess.run`

**Resultado esperado:**
- Chamada contém `["git", "push", "-u", "origin", "feature/minha-feature"]` (ou equivalente)

---

### CT-032 — `current_branch` retorna nome da branch atual

**User Story:** task04 — Leitura da branch corrente  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado para retornar `"feature/minha-feature\n"` no stdout

**Passos:**
1. Chamar `current_branch()`

**Resultado esperado:**
- Retorno é `"feature/minha-feature"` (sem whitespace)

---

### CT-033 — Erro do `git` CLI propagado como `RuntimeError` com mensagem do stderr

**User Story:** task04 — Tratamento de erros  
**Tipo:** unitário  

**Pré-condição:**
- `subprocess.run` mockado para lançar `subprocess.CalledProcessError` com stderr preenchido

**Passos:**
1. Chamar qualquer função do módulo (ex: `push("feature/x")`)

**Resultado esperado:**
- `RuntimeError` é lançado
- Mensagem do `RuntimeError` contém o conteúdo do stderr

---

### CT-034 — Todas as funções públicas acessíveis via `src.integrations.git`

**User Story:** task04 — Interface pública do módulo  
**Tipo:** unitário  

**Pré-condição:**
- Task01 e task04 executadas

**Passos:**
1. Executar:
   ```python
   from src.integrations.git import create_branch, commit, push, current_branch
   ```

**Resultado esperado:**
- Import sem erro
- Todos os símbolos são callable
