Status: approved
Owner: architecture-agent
Last updated: 2026-05-26

## Inputs
- docs/02-architecture/overview.md
- docs/01-requirements/meeting-01.md
- docs/01-requirements/github-setup.md

## Responsabilidade

Abstrai toda comunicação com a API do GitHub. Lê issues do backlog, move cards no board, posta comentários com resultados de agentes, detecta labels de aprovação e abre Pull Requests.

## Entradas

- Configuração do projeto (repo, board, labels) via `config/`
- Dados a postar (resultado de agente, status de etapa) via `orchestrator`
- Comandos de leitura (próxima issue, status de aprovação) via `orchestrator`

## Saídas

- Issue selecionada para processamento (id, título, labels, milestone)
- Status de aprovação do gate (aprovado / rejeitado / pendente)
- Confirmação de ações executadas (card movido, PR aberto, comentário postado)

## Dependências

- `gh` CLI autenticado na máquina
- `config` — leitura de repo, board e labels configurados
- Sem dependência de outros módulos internos
