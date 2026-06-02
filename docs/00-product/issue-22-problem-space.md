Status: draft
Owner: product-agent
Issue: #22
Last updated: 2026-06-02

## Inputs
- src/orchestrator/runner.py (linhas ~270-290)
- esteira.yml (boards.demanda.columns.analise-negocio)

## Contexto
O runner executa o agente, faz commit/push/PR e então move o card no board. A movimentação é feita chamando `github.move_card` com o nome da coluna atual (`col_name`). Em seguida, o state é salvo com `status = "awaiting_approval"`.

## Problema raiz
O `github.move_card` é chamado com `col_name` — o nome da coluna onde o agente acabou de rodar (ex: "Análise de Negócio") — mas o estado correto do processo neste momento já é a coluna seguinte (ex: "Aprovação Negócio"), pois o trabalho do agente está concluído e aguarda revisão humana.

Trecho atual problemático em `runner.py`:
```python
github.move_card(config, current_state["issue_number"], col_name, ...)
current_state["status"] = "awaiting_approval"
```

O card deveria ir para `_column_name(config, _advance(config, current_col))`.

## Impacto
- O board fica inconsistente com o estado real (`state.json` diz `awaiting_approval` mas o card está na coluna do agente)
- O humano não vê o card na coluna de aprovação e precisa movê-lo manualmente
- Risco de duplicidade se o humano mover e o runner também tentar mover

## Oportunidade
A correção é pontual e de baixo risco: substituir `col_name` por `_column_name(config, next_col_id)` na chamada `github.move_card` que precede `awaiting_approval`. Nenhuma mudança de estado, contrato ou interface é necessária.
