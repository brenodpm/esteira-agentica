Status: approved
Owner: architecture-agent
Last updated: 2026-05-26

## Inputs
- docs/00-product/vision.md
- docs/00-product/problem-space.md
- docs/00-product/epicos.md
- docs/01-requirements/meeting-01.md

## Visão geral

Sistema de orquestração automática de agentes de IA integrado ao GitHub e ao git local. Recebe itens de trabalho do backlog (GitHub Issues), aciona agentes em sequência conforme o fluxo definido, coleta métricas de execução e aguarda aprovação humana nos gates entre etapas. Toda interação com o usuário ocorre via GitHub, sem necessidade de acesso direto à máquina.

## Estilo arquitetural

**Monólito modular** com módulos bem delimitados e orquestrador central.

Justificativa: o sistema roda em uma única máquina, não há requisito de escala horizontal, e a separação em serviços independentes adicionaria complexidade sem benefício. Módulos separados garantem coesão e permitem evolução independente sem overhead de rede ou deploy distribuído.

## Componentes

| Componente | Responsabilidade |
|---|---|
| `orchestrator` | Sequenciar agentes, gerenciar estado da esteira, controlar gates de aprovação |
| `agents` | Módulos individuais de cada agente (product, requirements, architecture, etc.) |
| `integrations/github` | Ler/escrever issues, mover cards no board, abrir PRs, postar comentários |
| `integrations/git` | Criar branches, fazer commits, seguir gitflow configurado |
| `metrics` | Coletar e persistir custo em tokens, tempo de execução, retrabalho e delírios por agente/feature |
| `config` | Carregar e validar configurações por projeto (gitflow, board, agentes ativos) |

## Fluxo principal

```
GitHub Issues (backlog)
        │
        ▼
  [orchestrator]
        │
        ├─► lê próxima issue via integrations/github
        ├─► cria branch via integrations/git
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

## Fluxo de bloqueio

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
- Fluxo principal atualizado com mecanismo de bloqueio entre tasks
- Motivo: gap identificado — arquitetura não cobria dependências bloqueantes entre agentes ou com humano (ver adr-004)