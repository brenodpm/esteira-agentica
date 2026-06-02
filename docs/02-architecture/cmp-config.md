Status: approved
Owner: architecture-agent
Last updated: 2026-05-26

## Inputs
- docs/02-architecture/overview.md
- docs/01-requirements/meeting-01.md

## Responsabilidade

Carrega e valida a configuração do projeto. Fornece aos demais módulos os parâmetros de gitflow, board, repositório e sequência de agentes sem que esses módulos precisem conhecer o formato de armazenamento.

## Entradas

- Arquivo de configuração do projeto (ex: `config/project.json`) — definido pelo usuário na inicialização
- Valores padrão para parâmetros não configurados

## Saídas

- Configuração validada e tipada para consumo pelos módulos: repo, gitflow (branch base, prefixos), board (colunas, labels), sequência de agentes ativos

## Dependências

- `json` e `pathlib` (stdlib Python)
- Sem dependência de outros módulos internos
- Consumido por `orchestrator`, `integrations/github` e `integrations/git`
