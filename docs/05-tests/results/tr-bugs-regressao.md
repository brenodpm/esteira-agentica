Status: approved
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/05-tests/results/bug-task01-ct002-repo-vazio.md
- docs/05-tests/results/bug-task11-ct090-token-sem-escopo-project.md
- docs/05-tests/results/bug-task11-ct091-issues-nao-criadas.md
- docs/05-tests/tc-task01-estrutura-projeto.md
- docs/05-tests/tc-task11-setup-github.md

## Feature
Verificação de bugs resolvidos + regressiva básica

---

## Execução

### CT-002 — `python -m src` executa sem erro e imprime versão

**Bug:** bug-task01-ct002-repo-vazio.md  
**Resultado:** passed

**Observações:**
- `python -m src` retorna exit code 0
- Saída: `0.1.0`
- `config/project.json` contém `"repo": "brenodpm/esteira-agentica"` (não vazio)
- Bug resolvido confirmado

---

### CT-090 — Board "Esteira Agêntica" verificável via CLI

**Bug:** bug-task11-ct090-token-sem-escopo-project.md  
**Resultado:** failed

**Observações:**
- `gh project list --owner brenodpm` retorna:
  `GraphQL: Resource not accessible by personal access token (user.projectsV2.nodes.0)`
- Token PAT ativo ainda não possui escopo `project` (classic) ou permissão `Projects: Read and write` (fine-grained)
- Bug permanece aberto — requer recriar o token conforme `docs/06-decisions-log/nota-github-token-permissoes.md`

---

### CT-091 — Issues iniciais criadas e associadas ao milestone correto

**Bug:** bug-task11-ct091-issues-nao-criadas.md  
**Resultado:** passed

**Observações:**
- `gh issue list --repo brenodpm/esteira-agentica --state all` retorna 11 issues abertas
- Distribuição por milestone:
  - Orquestração Automática de Agentes: 3 issues (`epic:orquestracao`)
  - Gestão de Tarefas: 2 issues (`epic:gestao-tarefas`)
  - Integração com Git: 2 issues (`epic:integracao-git`)
  - Coleta de Métricas: 3 issues (`epic:metricas`)
  - Operação Remota: 1 issue (`epic:operacao-remota`)
- Bug resolvido confirmado

---

## Regressiva básica

### CT-001 — Estrutura de diretórios corresponde ao definido

**Resultado:** passed

**Observações:**
- Diretórios presentes: `src/orchestrator/`, `src/agents/`, `src/integrations/`, `src/integrations/github/`, `src/integrations/git/`, `src/metrics/`, `src/config/`
- Todos contêm `__init__.py`
- `src/__main__.py` existe

---

### CT-003 — `pyproject.toml` válido com campos obrigatórios

**Resultado:** passed

**Observações:**
- TOML válido, sem exceção
- `name`: `esteira-agentica`
- `version`: `0.1.0`
- `requires-python`: `>=3.11`

---

### CT-004 — `config/project.json` válido com todos os campos padrão

**Resultado:** passed

**Observações:**
- JSON válido, sem exceção
- Chaves presentes: `repo`, `gitflow`, `board`, `agents_sequence`
- `gitflow.branch_base`: `main`
- `gitflow.prefixes`: `feature`, `fix`, `release`, `hotfix`
- `board.columns`: `Backlog`, `In Progress`, `Done`

---

### CT-005 — `state.json` existe com estrutura inicial correta

**Resultado:** passed

**Observações:**
- JSON válido, sem exceção
- Conteúdo: `{"current_feature": null, "current_step": null, "status": "idle"}`

---

### CT-006 — `.gitignore` cobre entradas obrigatórias

**Resultado:** passed

**Observações:**
- `__pycache__/` presente
- `*.pyc` presente
- `metrics.db` presente
- `.env` presente

---

### CT-087 — Labels por épico existem no repositório

**Resultado:** passed

**Observações:**
- Labels presentes: `epic:orquestracao`, `epic:gestao-tarefas`, `epic:integracao-git`, `epic:metricas`, `epic:operacao-remota`

---

### CT-088 — Labels operacionais do sistema existem no repositório

**Resultado:** passed

**Observações:**
- Labels presentes: `blocked` (#b60205), `needs-human` (#e99695), `approved` (#0e8a16), `rejected` (#b60205)

---

### CT-089 — 5 milestones criados, um por épico

**Resultado:** passed

**Observações:**
- 5 milestones com `state: open`:
  - Orquestração Automática de Agentes
  - Gestão de Tarefas
  - Integração com Git
  - Coleta de Métricas
  - Operação Remota

---

### CT-093 — `gh auth status` confirma autenticação

**Resultado:** passed

**Observações:**
- `Logged in to github.com account brenodpm`
- Token ativo com escopos suficientes para issues, labels, milestones
- ⚠️ Escopo `project` ausente (ver CT-090)

---

## Resumo

- Total: 12
- Passou: 11
- Falhou: 1 (CT-090 — token sem escopo project)

## Bugs em aberto após execução

| Bug | CT | Status |
|-----|----|--------|
| bug-task11-ct090-token-sem-escopo-project.md | CT-090 | open — requer recriar token PAT com escopo `project` |
