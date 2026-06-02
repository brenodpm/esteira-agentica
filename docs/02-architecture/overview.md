Status: approved
Owner: architecture-agent
Last updated: 2026-05-31

## Inputs
- docs/00-product/vision.md
- docs/00-product/problem-space.md
- docs/00-product/epicos.md
- docs/01-requirements/meeting-01.md

## Visão geral

Sistema de orquestração automática de agentes de IA integrado ao GitHub e ao git local. Recebe itens de trabalho do backlog (GitHub Issues), aciona agentes em sequência conforme o fluxo definido em `esteira.yml`, coleta métricas de execução e aguarda aprovação humana nos gates entre etapas. Toda interação com o usuário ocorre via GitHub, sem necessidade de acesso direto à máquina.

## Estilo arquitetural

**Monólito modular** com módulos bem delimitados e orquestrador central.

Justificativa: o sistema roda em uma única máquina, não há requisito de escala horizontal, e a separação em serviços independentes adicionaria complexidade sem benefício. Módulos separados garantem coesão e permitem evolução independente sem overhead de rede ou deploy distribuído.

## Configuração central — `esteira.yml`

O arquivo `esteira.yml` na raiz do projeto é a **única fonte de verdade** para configuração da esteira. Substitui `config/project.json`.

Campos obrigatórios:

| Campo | Tipo | Descrição |
|---|---|---|
| `git.repo` | string | Repositório GitHub (`owner/repo`) |
| `doc` | string | Diretório base da documentação |
| `boards` | map | Boards com colunas, agentes e fluxo de transição |

Campos opcionais:

| Campo | Tipo | Descrição |
|---|---|---|
| `git.flow` | map | Gitflow customizado (branches, prefixos, merge targets) |
| `pipe.agent.timeout` | int | Timeout em minutos por agente |
| `pipe.agent.sleeptime` | int | Dormência em minutos quando sem tasks |

O loader (`src/config/loader.py`) valida os campos obrigatórios e aplica defaults para os opcionais. Ver ADR-008.

## Componentes

| Componente | Responsabilidade |
|---|---|
| `esteira.yml` | Configuração central: repo, gitflow, boards, agentes e timeouts |
| `orchestrator` | Sequenciar agentes, gerenciar estado da esteira, controlar gates de aprovação |
| `.kiro/agents/` | Definição executável dos agentes Kiro (product, requirements, architecture, tech-lead, engineering, quality) — ver ADR-007 |
| `integrations/github` | Ler/escrever issues, mover cards no board, abrir PRs, postar comentários |
| `integrations/git` | Criar branches, fazer commits, seguir gitflow configurado em `esteira.yml` |
| `metrics` | Coletar e persistir custo em tokens, tempo de execução, retrabalho e delírios por agente/feature |
| `config` | Carregar e validar `esteira.yml`; expor configuração normalizada para os demais módulos |

## Fluxo principal

```
esteira.yml (config)
        │
        ▼
GitHub Issues (backlog)
        │
        ▼
  [orchestrator]
        │
        ├─► lê próxima issue via integrations/github
        ├─► cria branch via integrations/git (gitflow de esteira.yml)
        │
        ▼
  aciona agente (agents/<role>)
        │
        ├─► agente executa e produz artefato
        ├─► metrics registra tokens + tempo
        │
        ▼
  gate de aprovação
        │
        ├─► posta resultado na issue (integrations/github)
        ├─► aguarda label/comentário de aprovação
        │
        ▼
  próximo agente (repete até conclusão)
        │
        ▼
  integrations/git → commit + PR
  integrations/github → fecha issue / move card
        │
        ├─► ao concluir: verifica issues com label `blocked` desbloqueadas → remove label, recoloca no backlog
```

## Fluxo de bloqueio

```
  agente detecta dependência bloqueante
        │
        ├─► cria issue bloqueante (agente ou `needs-human`)
        ├─► adiciona label `blocked` na issue corrente com referência à bloqueante
        │
        ▼
  orquestrador detecta `blocked` → pula para próxima issue disponível
        │
        ▼
  issue bloqueante é concluída → orquestrador remove `blocked` da dependente → volta ao backlog
```

## Changes
- Componente `config` atualizado: fonte de verdade é `esteira.yml`, não `config/project.json`
- Tabela de campos obrigatórios/opcionais do `esteira.yml` adicionada
- Referência ao ADR-008 adicionada
- Fluxo principal atualizado para mostrar `esteira.yml` como ponto de entrada de configuração
- Motivo: ADR-008 formalizou `esteira.yml` como config base (substitui `config/project.json`)
