Status: approved
Owner: architecture-agent
Last updated: 2026-05-26

## Inputs
- docs/02-architecture/overview.md
- docs/02-architecture/adr-002-mecanismo-orquestracao.md
- docs/02-architecture/adr-003-persistencia-estado-metricas.md

## Responsabilidade

Ponto central de controle da esteira. Sequencia os agentes conforme o fluxo definido, gerencia o estado da execução, controla os gates de aprovação humana e garante retomada após interrupção.

## Entradas

- `state.json` — estado atual da execução (etapa, feature, resultado do último agente)
- Configuração do projeto (`config/`) — sequência de agentes, gitflow, board
- Sinal de aprovação — label adicionada à issue no GitHub (lido via `integrations/github`)

## Saídas

- `state.json` atualizado a cada transição
- Invocação do próximo agente via `subprocess` (Kiro CLI)
- Registro de execução em `metrics.db` (via `metrics`)
- Postagem de resultado na issue (via `integrations/github`)

## Dependências

- `config` — leitura da configuração do projeto
- `integrations/github` — leitura de aprovação e postagem de resultados
- `integrations/git` — criação de branch ao iniciar feature
- `metrics` — registro de cada execução de agente
- `agents/*` — invocados via subprocess
