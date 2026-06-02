Status: open
Owner: architecture-agent
Last updated: 2026-05-26

## Inputs
- docs/02-architecture/adr-002-mecanismo-orquestracao.md
- docs/02-architecture/constraints.md

## Descrição

Avaliar como paralelizar a execução da esteira. A v1 é estritamente sequencial (um agente por vez, uma feature por vez) por simplicidade e pela restrição de single-machine. Em versões futuras, pode ser viável paralelizar em diferentes níveis:

- **Features em paralelo:** múltiplas features sendo processadas simultaneamente
- **Agentes em paralelo:** etapas independentes de uma mesma feature executando ao mesmo tempo
- **Múltiplas máquinas:** distribuir a carga entre instâncias

> **Incerteza:** paralelismo introduz complexidade de estado compartilhado, concorrência no `metrics.db` e potencial conflito de contexto entre agentes. Não é claro qual nível de paralelismo traz mais benefício com menor risco. Precisa ser amadurecido quando a v1 estiver estável.

## Impacto

Sem paralelismo, o throughput da esteira é limitado a uma feature por vez. Para times com backlog grande, isso pode ser um gargalo relevante.

## Responsável pela resolução

architecture-agent

## Bloqueia etapa?

Não — evolução futura, não bloqueia a v1.
