Status: resolved
Owner: quality-agent
Last updated: 2026-05-28

## Inputs
- docs/05-tests/tc-task11-setup-github.md — CT-090
- docs/04-tasks/task11-setup-github.md
- docs/06-decisions-log/nota-github-token-permissoes.md

## Descrição
O token PAT configurado não possui escopo `project`, impedindo verificação e operação do board via `gh` CLI. O comando `gh project list --owner brenodpm` retorna erro de permissão.

## Passos para reproduzir
1. Executar `gh project list --owner brenodpm`

## Resultado esperado
- Lista de projetos do owner, incluindo "Esteira Agêntica"

## Resultado obtido
- `GraphQL: Resource not accessible by personal access token (user.projectsV2.nodes.0)`

## Severidade
medium

## Violação
- requisito (task11 — board deve ser verificável e operável via CLI)
