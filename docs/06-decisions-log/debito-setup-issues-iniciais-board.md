Status: open
Owner: quality-agent
Last updated: 2026-05-28

## Inputs
- docs/05-tests/tc-task11-setup-github.md — CT-091, CT-092
- docs/04-tasks/task11-setup-github.md
- docs/05-tests/results/bug-task11-ct091-issues-nao-criadas.md

## Descrição

As 11 issues iniciais definidas na task11 não foram criadas no repositório `brenodpm/esteira-agentica`. Como consequência, o board "Esteira Agêntica" não foi populado (CT-092 bloqueado por CT-091).

A criação manual das issues e associação ao board foi adiada intencionalmente para ser feita de forma estruturada — preferencialmente via script ou pela própria esteira após estabilização da v1.

## Itens pendentes

- Criar 11 issues distribuídas pelos 5 milestones com labels de épico correspondentes
- Adicionar todas as issues ao board na coluna `Backlog`

## Impacto

Sem as issues, o board não reflete o backlog real do projeto. Não bloqueia o desenvolvimento da v1.

## Responsável pela resolução

engineering-agent (execução pós v1)

## Bloqueia etapa?

Não — pós v1.
