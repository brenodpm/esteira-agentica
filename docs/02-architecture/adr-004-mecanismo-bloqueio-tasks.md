Status: accepted
Owner: architecture-agent
Last updated: 2026-05-26

## Inputs
- docs/02-architecture/overview.md
- docs/02-architecture/adr-002-mecanismo-orquestracao.md
- docs/01-requirements/meeting-01.md

## Contexto

Durante a execução, um agente pode encontrar uma dependência bloqueante que só pode ser resolvida por uma etapa anterior (outro agente) ou por intervenção humana. O fluxo linear original não cobria esse caminho de retorno.

## Decisão

Bloqueios são modelados como metadados nas issues do GitHub:

- O agente bloqueado **cria uma nova issue** descrevendo o que precisa ser resolvido (bloqueante), com label `blocked-by` apontando para a issue bloqueante
- O agente bloqueado **adiciona label `blocked`** na sua própria issue
- O orquestrador, ao encontrar uma issue com label `blocked`, **pula para a próxima issue disponível** no backlog
- Quando a issue bloqueante é concluída, o orquestrador **remove a label `blocked`** da issue dependente, recolocando-a no backlog
- Para bloqueios que requerem intervenção humana, o agente cria a issue bloqueante com label `needs-human` — o orquestrador não a processa automaticamente; aguarda resolução manual

## Justificativa

- Reutiliza o GitHub Issues como mecanismo de coordenação já existente — sem estrutura adicional
- O orquestrador não precisa conhecer a topologia de dependências antecipadamente; descobre em runtime via labels
- Bloqueios humanos e bloqueios de agente são distinguidos por label, sem lógica especial no orquestrador
- Compatível com o `state.json` existente — o orquestrador simplesmente registra a issue como `blocked` e avança

## Consequências

- Positivas: dependências entre tasks visíveis no board; sem acoplamento entre agentes; humano pode resolver bloqueios remotamente via GitHub
- Negativas: orquestrador precisa verificar, ao concluir cada issue, se alguma issue bloqueada foi desbloqueada
- Riscos: ciclo de bloqueio mútuo (A bloqueia B, B bloqueia A) — orquestrador deve detectar e escalar para humano via `needs-human`
