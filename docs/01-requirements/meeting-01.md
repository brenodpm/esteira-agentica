# Requisitos — Primeira Reunião

Status: approved
Owner: requirements-agent
Last updated: 2026-05-14T22:14:00-03:00

## Inputs
- startup.md
- docs/00-product/vision.md
- docs/00-product/problem-space.md
- docs/00-product/epicos.md

## Decisões aprovadas

| Decisão | Definição |
|---|---|
| Arquitetura | Módulos separados + orquestrador central |
| Linguagem | A definir pelo arquiteto |
| Persistência local | Sim (estado da orquestração + métricas) |
| Gitflow padrão | Completo: `main`, `develop`, `release/*`, `hotfix/*`, `feature/*`, `fix/*` |
| Gitflow configurável | Sim, por projeto |
| Board padrão | Backlog / In Progress / Done |
| Board configurável | Sim, por projeto |
| Labels por épico | Sim |
| Ferramenta de gestão | GitHub Issues + GitHub Projects |

## Estrutura de pastas

```
src/
├── orchestrator/   # lógica de orquestração e sequenciamento de agentes
├── agents/         # módulos individuais de cada agente
├── integrations/
│   ├── github/     # integração com GitHub Issues/Projects/PRs
│   └── git/        # operações de versionamento
├── metrics/        # coleta de tokens, tempo, retrabalho, delírios
└── config/         # configurações por projeto (gitflow, board, etc.)
```

## Requisitos abertos

- Linguagem/runtime: aguarda decisão do arquiteto
- Estrutura interna dos módulos: aguarda decisão do arquiteto
