Status: approved
Owner: product-agent
Last updated: 2026-05-28

## Inputs
- docs/00-product/vision.md
- docs/00-product/problem-space.md
- docs/06-decisions-log/debito-product-plano-migracao-generico.md

---

## Objetivo

Guia para qualquer time adotar a esteira agêntica em um projeto existente ou novo, de forma incremental e sem big-bang.

---

## Pré-requisitos

### Ferramentas obrigatórias

| Ferramenta | Versão mínima | Instalação |
|------------|---------------|------------|
| Git | 2.x | https://git-scm.com |
| GitHub CLI (`gh`) | 2.x | https://cli.github.com |
| Kiro CLI | latest | https://kiro.dev |
| Python | 3.11+ | https://python.org |

### Contas e acessos

- Conta GitHub com repositório criado
- GitHub token com escopos: `repo`, `project`, `read:org`
- Kiro CLI autenticado (`kiro-cli auth`)

### Verificação rápida

```bash
git --version
gh --version
kiro-cli --version
python --version
gh auth status
```

---

## Diagnóstico do estado atual

Antes de migrar, identifique o que o time já tem:

| Item | Tem? | Ação |
|------|------|------|
| Repositório Git | ✓/✗ | Se não: `gh repo create` |
| Board de tarefas (GitHub Projects) | ✓/✗ | Se não: criar via `scripts/setup-github.sh` |
| Estrutura `docs/` com artefatos de produto | ✓/✗ | Se não: copiar template |
| `config/project.json` configurado | ✓/✗ | Se não: ver seção abaixo |
| Agentes Kiro em `.kiro/agents/` | ✓/✗ | Se não: copiar de `.kiro/agents/` deste repo |

---

## Passos de adoção incremental

### Fase 1 — Setup (30min)

1. Clonar ou criar repositório
2. Copiar os agentes Kiro para o projeto:
   ```bash
   cp -r esteira-agentica/.kiro/agents/ .kiro/agents/
   ```
   Os agentes são genéricos — funcionam em qualquer projeto, independente de estrutura de pastas ou linguagem.
3. Autenticar Kiro CLI:
   ```bash
   kiro-cli auth
   ```
4. (Opcional) Configurar GitHub board:
   ```bash
   bash scripts/setup-github.sh
   ```

### Fase 2 — Primeiro ciclo com a esteira (1 sprint)

1. Iniciar pelo **product agent**: definir vision.md, problem-space.md, epicos.md
2. Avançar para **requirements agent**: user stories e regras de negócio
3. Usar o board para rastrear progresso
4. Aprovar gates manualmente antes de avançar de etapa

### Fase 3 — Automação progressiva

- Configurar orquestrador para acionar agentes automaticamente
- Ativar coleta de métricas de tokens
- Ajustar `config/project.json` conforme necessidade do projeto

---

## Configuração por projeto (`config/project.json`)

```json
{
  "project": "nome-do-projeto",
  "github_owner": "usuario-ou-org",
  "github_repo": "nome-do-repositorio",
  "board_name": "Nome do Board",
  "milestones": ["v0.1", "v0.2", "v1.0"],
  "default_branch": "main",
  "develop_branch": "develop"
}
```

---

## Checklist de pré-requisitos

```
[ ] git instalado e configurado (user.name, user.email)
[ ] gh instalado e autenticado
[ ] kiro-cli instalado e autenticado
[ ] Python 3.11+ instalado
[ ] Repositório GitHub criado
[ ] Token com escopos: repo, project, read:org
[ ] config/project.json preenchido
[ ] .kiro/agents/ copiado para o projeto
[ ] docs/agents/ copiado para o projeto
```

---

## Variações de contexto de adoção

### Time que já usa CI/CD tradicional
- Manter pipeline existente
- Adicionar a esteira como camada de geração de artefatos (docs, código)
- Gates de aprovação humana substituem code review manual

### Time que já usa outra esteira de IA
- Mapear papéis existentes para os agentes desta esteira
- Migrar artefatos de produto existentes para `docs/00-product/`
- Adotar incrementalmente, começando pelo product agent

### Projeto novo (greenfield)
- Seguir Fase 1 → 2 → 3 sem adaptações
- Usar este repo como template

---

## Incertezas conhecidas

> Este plano foi validado com um caso real (este próprio projeto). Variações de contexto externas ainda não foram testadas. Ajustes serão necessários conforme adotantes externos reportarem fricções.

---

## Changes
- Criado como resolução do débito debito-product-plano-migracao-generico.md
