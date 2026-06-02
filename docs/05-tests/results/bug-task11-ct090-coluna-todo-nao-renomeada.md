Status: resolved
Owner: quality-agent
Last updated: 2026-05-28

## Inputs
- docs/05-tests/tc-task11-setup-github.md — CT-090
- docs/04-tasks/task11-setup-github.md

## Descrição
A coluna `"Todo"` do board "Esteira Agêntica" não foi renomeada para `"Backlog"`. O campo Status do projeto contém as opções `Todo`, `In progress`, `Done` em vez de `Backlog`, `In Progress`, `Done`.

## Passos para reproduzir
1. Executar `gh project field-list 3 --owner brenodpm`
2. Identificar o ID do campo `Status` (tipo `ProjectV2SingleSelectField`)
3. Executar:
   ```
   gh api graphql -f query='{ node(id: "PVTSSF_lAHOAsuYmc4BY_JuzhUBC-Q") { ... on ProjectV2SingleSelectField { name options { name } } } }'
   ```

## Resultado esperado
- Opções do campo Status: `Backlog`, `In Progress`, `Done`
- Coluna `"Todo"` não existe

## Resultado obtido
- Opções do campo Status: `Todo`, `In progress`, `Done`
- Coluna `"Backlog"` não existe

## Severidade
low

## Violação
- requisito (task11 — coluna "Todo" deve ser renomeada para "Backlog")
