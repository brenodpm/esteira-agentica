Status: accepted
Owner: architecture-agent
Last updated: 2026-05-27

## Inputs
- docs/02-architecture/adr-002-mecanismo-orquestracao.md
- docs/02-architecture/adr-004-mecanismo-bloqueio-tasks.md

## Contexto

O orquestrador precisa de uma regra clara para decidir qual item processar a seguir. Sem prioridade definida, corre o risco de iniciar trabalho novo enquanto trabalho em andamento está incompleto, gerando desperdício e contexto fragmentado.

## Decisão

O orquestrador segue a hierarquia do GitHub de baixo para cima ao selecionar o próximo item:

1. **Sub-issues em andamento** (In Progress) — concluir antes de qualquer outra coisa
2. **Sub-issues no backlog** do milestone corrente — esgotar antes de avançar
3. **Issues do milestone corrente** sem sub-issues pendentes — processar na ordem do board
4. **Novo milestone** — só iniciar quando o milestone corrente não tiver issues nem sub-issues abertas no backlog ou em andamento

Regras complementares:
- Items com label `blocked` são pulados e recolocados no backlog automaticamente quando desbloqueados
- Items com label `needs-human` não são processados pelo orquestrador — aguardam resolução humana
- Em caso de empate dentro do mesmo nível, priorizar pela ordem de criação (mais antiga primeiro)

## Justificativa

- Evita iniciar trabalho novo com trabalho incompleto em aberto — reduz contexto fragmentado e retrabalho
- Respeita a granularidade natural do GitHub: sub-issue é parte de uma issue, que é parte de um milestone
- Simples de implementar: o orquestrador consulta o board em ordem de hierarquia antes de selecionar

## Consequências

- Positivas: foco em conclusão antes de expansão; menor WIP (work in progress); progresso visível no board
- Negativas: um milestone com muitas sub-issues pode atrasar o início do próximo por tempo considerável
- Riscos: sub-issue bloqueada indefinidamente pode travar o milestone inteiro — mitigado pela regra de pular `blocked` e escalar `needs-human`
