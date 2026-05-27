Status: open
Owner: architecture-agent
Last updated: 2026-05-27

## Inputs
- docs/04-tasks/task07-modulo-orchestrator.md
- docs/02-architecture/adr-002-mecanismo-orquestracao.md
- docs/02-architecture/adr-004-mecanismo-bloqueio-tasks.md

## Descrição

Definir o tempo de dormência do orquestrador nos dois cenários em que não há trabalho disponível:

1. **Backlog vazio** — `get_next_issue` retorna `None`; não há features para processar
2. **Todas as issues bloqueadas** — todas as issues do backlog possuem label `blocked` ou `needs-human`; nenhuma é elegível

A v1 usa `poll_interval_s = 60` como padrão fixo em `run_loop`, sem distinção entre os dois cenários. Questões em aberto:

- O intervalo deve ser o mesmo para os dois casos? Backlog vazio pode tolerar dormência maior; bloqueios podem ser resolvidos mais rapidamente.
- O intervalo deve ser configurável em `config/project.json`?
- Deve haver backoff exponencial após N iterações sem trabalho, para reduzir chamadas desnecessárias à API do GitHub?
- Qual o limite de rate do `gh` CLI que precisa ser respeitado?

## Impacto

Com intervalo fixo de 60s e backlog vazio por horas, o orquestrador faz chamadas desnecessárias à API do GitHub. Com intervalo muito longo, a retomada após desbloqueio de uma issue tem latência perceptível.

## Responsável pela resolução

architecture-agent

## Bloqueia etapa?

Não — o valor padrão de 60s é funcional para a v1. Decisão deve ser tomada antes de qualquer uso em produção com backlog de alta rotatividade.
