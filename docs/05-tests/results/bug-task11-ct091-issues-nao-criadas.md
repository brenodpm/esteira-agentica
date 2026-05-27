Status: open
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/05-tests/tc-task11-setup-github.md — CT-091, CT-092
- docs/04-tasks/task11-setup-github.md

## Descrição
O setup do repositório GitHub não criou as 11 issues iniciais definidas na task11. O repositório `brenodpm/esteira-agentica` não contém nenhuma issue em nenhum estado.

## Passos para reproduzir
1. Executar `gh issue list --repo brenodpm/esteira-agentica --state all`

## Resultado esperado
- 11 issues abertas distribuídas pelos 5 milestones com labels de épico correspondentes

## Resultado obtido
- 0 issues retornadas

## Severidade
high

## Violação
- requisito (task11 — issues iniciais por épico devem ser criadas durante o setup)
