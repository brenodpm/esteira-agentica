Status: draft
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/04-tasks/task11-setup-github.md
- docs/01-requirements/github-setup.md

## Feature
Setup inicial do repositório GitHub (labels, milestones, board, issues)

## Casos de teste

> **Tipo predominante:** manual — verificação pós-execução via `gh` CLI.  
> Pré-condição global: `gh auth status` confirma autenticação no repositório `brenodpm/esteira-agentica`.

---

### CT-087 — Labels por épico existem no repositório

**User Story:** task11 — Labels de épico criadas  
**Tipo:** manual  

**Pré-condição:**
- Setup executado conforme task11

**Passos:**
1. Executar `gh label list --repo brenodpm/esteira-agentica`

**Resultado esperado:**
- Lista contém exatamente as labels: `epic:orquestracao`, `epic:gestao-tarefas`, `epic:integracao-git`, `epic:metricas`, `epic:operacao-remota`
- Cores e descrições correspondem às definidas na task

---

### CT-088 — Labels operacionais do sistema existem no repositório

**User Story:** task11 — Labels operacionais criadas  
**Tipo:** manual  

**Pré-condição:**
- Setup executado conforme task11

**Passos:**
1. Executar `gh label list --repo brenodpm/esteira-agentica`

**Resultado esperado:**
- Lista contém: `blocked`, `needs-human`, `approved`, `rejected`
- Cores correspondem às definidas na task (`blocked` e `rejected` em `#b60205`, `approved` em `#0e8a16`, `needs-human` em `#e99695`)

---

### CT-089 — 5 milestones criados, um por épico

**User Story:** task11 — Milestones por épico  
**Tipo:** manual  

**Pré-condição:**
- Setup executado conforme task11

**Passos:**
1. Executar `gh api repos/brenodpm/esteira-agentica/milestones`

**Resultado esperado:**
- Retorna exatamente 5 milestones com títulos:
  - `Orquestração Automática de Agentes`
  - `Gestão de Tarefas`
  - `Integração com Git`
  - `Coleta de Métricas`
  - `Operação Remota`
- Todos com `state: "open"`

---

### CT-090 — Board "Esteira Agêntica" criado com colunas corretas

**User Story:** task11 — Board de acompanhamento  
**Tipo:** manual  

**Pré-condição:**
- Setup executado conforme task11

**Passos:**
1. Executar `gh project list --owner brenodpm`
2. Acessar o board via UI do GitHub

**Resultado esperado:**
- Projeto `"Esteira Agêntica"` listado
- Board contém colunas: `Backlog`, `In Progress`, `Done`
- Coluna `"Todo"` não existe (renomeada para `"Backlog"`)

---

### CT-091 — Issues iniciais criadas e associadas ao milestone correto

**User Story:** task11 — Issues iniciais por épico  
**Tipo:** manual  

**Pré-condição:**
- Setup executado conforme task11

**Passos:**
1. Executar `gh issue list --repo brenodpm/esteira-agentica --state open` para cada milestone

**Resultado esperado:**
- Milestone `Orquestração Automática de Agentes`: 3 issues abertas com label `epic:orquestracao`
- Milestone `Gestão de Tarefas`: 2 issues abertas com label `epic:gestao-tarefas`
- Milestone `Integração com Git`: 2 issues abertas com label `epic:integracao-git`
- Milestone `Coleta de Métricas`: 3 issues abertas com label `epic:metricas`
- Milestone `Operação Remota`: 1 issue aberta com label `epic:operacao-remota`
- Total: 11 issues abertas

---

### CT-092 — Issues iniciais adicionadas ao board

**User Story:** task11 — Issues visíveis no board  
**Tipo:** manual  

**Pré-condição:**
- Setup executado conforme task11

**Passos:**
1. Acessar o board `"Esteira Agêntica"` via UI do GitHub

**Resultado esperado:**
- Todas as 11 issues iniciais aparecem na coluna `Backlog`
- Nenhuma issue aparece em `In Progress` ou `Done`

---

### CT-093 — `gh auth status` confirma autenticação antes da execução

**User Story:** task11 — Pré-requisito de autenticação  
**Tipo:** manual  

**Pré-condição:**
- Máquina com `gh` instalado

**Passos:**
1. Executar `gh auth status`

**Resultado esperado:**
- Saída indica `Logged in to github.com` com conta `brenodpm`
- Token tem escopo suficiente para criar labels, milestones, issues e projects
