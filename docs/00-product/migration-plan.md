Status: approved
Owner: product-agent
Last updated: 2026-05-31

## Inputs
- docs/00-product/vision.md
- docs/00-product/problem-space.md
- docs/06-decisions-log/debito-product-plano-migracao-generico.md
- docs/02-architecture/adr-008-esteira-yml-como-config-base.md

---

## Objetivo

Guia para qualquer time adotar a esteira agêntica em um projeto existente ou novo, de forma incremental e sem big-bang.

---

## Pré-requisitos

### Ferramentas obrigatórias

| Ferramenta | Versão mínima | Papel na esteira | Instalação |
|------------|---------------|------------------|------------|
| Git | 2.x | Versionamento de artefatos e código | https://git-scm.com |
| GitHub CLI (`gh`) | 2.x | Criar issues, mover cards, abrir PRs | https://cli.github.com |
| Kiro CLI | latest | Runtime de execução dos agentes | https://kiro.dev |
| Python | 3.11+ | Orquestrador e scripts de setup | https://python.org |
| PyYAML | 6.x | Leitura do `esteira.yml` | `pip install pyyaml` |

### Contas e acessos

- Conta GitHub com repositório criado
- GitHub token com escopos: `repo`, `project`, `read:org`
- Kiro CLI autenticado (`kiro auth`)

### Instalação passo a passo

```bash
# 1. Git
git --version  # verificar se já instalado
# Se não: https://git-scm.com/downloads

# 2. GitHub CLI
gh --version  # verificar se já instalado
# Se não (Linux): sudo apt install gh  ou  brew install gh (macOS)
# Autenticar: gh auth login

# 3. Kiro CLI
kiro --version  # verificar se já instalado
# Instalar: https://kiro.dev/docs/getting-started
# Autenticar: kiro auth

# 4. Python + PyYAML
python --version  # verificar se já instalado (3.11+)
pip install pyyaml
```

### Verificação rápida

```bash
git --version
gh --version
kiro --version
python --version
gh auth status
python -c "import yaml; print('PyYAML ok')"
```

---

## Configuração do projeto — `esteira.yml`

O arquivo `esteira.yml` na raiz do projeto é a **única fonte de verdade** para configuração da esteira.

### Campos obrigatórios

```yaml
doc: docs/                    # diretório base da documentação
git:
  repo: "owner/repo"          # repositório GitHub
boards:
  <id>:                       # ao menos um board
    name: <nome>
    todo: <coluna-inicial>
    columns:
      <id>:
        name: <nome>
```

### Exemplo mínimo funcional

```yaml
doc: docs/
git:
  repo: "meu-usuario/meu-projeto"
boards:
  task:
    name: Tarefas
    todo: backlog
    columns:
      backlog:
        name: Backlog
        change:
          executar: em-progresso
          cancelar: cancelado
      em-progresso:
        name: Em Progresso
        agent: engineering
        acao: "Implementar a tarefa"
        change:
          concluir: concluido
      concluido:
        name: Concluído
      cancelado:
        name: Cancelado
```

### Exemplo completo (com gitflow e pipe)

Ver `esteira.yml` na raiz deste repositório como referência.

---

## Diagnóstico do estado atual

Antes de migrar, identifique o que o time já tem:

| Item | Tem? | Ação |
|------|------|------|
| Repositório Git | ✓/✗ | Se não: `gh repo create` |
| Board de tarefas (GitHub Projects) | ✓/✗ | Se não: criar via `scripts/setup-github.sh` |
| Estrutura `docs/` com artefatos de produto | ✓/✗ | Se não: copiar template |
| `esteira.yml` configurado | ✓/✗ | Se não: ver seção acima |
| Agentes Kiro em `.kiro/agents/` | ✓/✗ | Se não: copiar de `.kiro/agents/` deste repo |

---

## Passos de adoção incremental

### Fase 1 — Setup (30min)

1. Clonar ou criar repositório
2. Criar `esteira.yml` na raiz com a configuração do projeto (ver exemplo acima)
3. Copiar os agentes Kiro para o projeto:
   ```bash
   cp -r esteira-agentica/.kiro/ .kiro/
   ```
   Os agentes são genéricos — funcionam em qualquer projeto, independente de estrutura de pastas ou linguagem.
4. Autenticar Kiro CLI:
   ```bash
   kiro auth
   ```
5. (Opcional) Configurar GitHub board:
   ```bash
   bash scripts/setup-github.sh
   ```

### Fase 2 — Primeiro ciclo com a esteira (1 sprint)

1. Iniciar pelo **product agent**: definir `vision.md`, `problem-space.md`, `epicos.md`
2. Avançar para **requirements agent**: user stories e regras de negócio
3. Usar o board para rastrear progresso
4. Aprovar gates manualmente antes de avançar de etapa

### Fase 3 — Automação progressiva

- Configurar orquestrador para acionar agentes automaticamente
- Ativar coleta de métricas de tokens
- Ajustar `esteira.yml` conforme necessidade do projeto (boards, gitflow, timeouts)

---

## Checklist de pré-requisitos

```
[ ] git instalado e configurado (user.name, user.email)
[ ] gh instalado e autenticado
[ ] kiro instalado e autenticado
[ ] Python 3.11+ instalado
[ ] PyYAML instalado (pip install pyyaml)
[ ] Repositório GitHub criado
[ ] Token com escopos: repo, project, read:org
[ ] esteira.yml criado na raiz do projeto
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
- Referência a `config/project.json` substituída por `esteira.yml` em todos os passos
- Adicionado PyYAML como dependência obrigatória
- Seção de configuração expandida com campos obrigatórios, exemplo mínimo e referência ao exemplo completo
- Checklist atualizado: `esteira.yml` no lugar de `config/project.json`
- Motivo: ADR-008 formalizou `esteira.yml` como única fonte de verdade de configuração
