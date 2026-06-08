# Relatório de Qualidade — Issue #22

**Bug:** Movimentação incorreta dos cards no board  
**Data:** 2026-06-08  
**Status:** ✅ Corrigido e validado

---

## Causa raiz

Dois problemas identificados em `src/orchestrator/runner.py`:

1. **Após execução do agente, `move_card` usava a coluna atual** — quando o agente termina em uma coluna cujo `advance` aponta para um gate humano (coluna sem agente), o card deveria mover para a coluna de aprovação. O código original chamava `move_card` com `col_name` (coluna onde o agente rodou), mantendo o card na posição errada.

2. **Teste CT-066 com asserção incorreta** — esperava `current_step == "product"` após aprovação no gate humano, mas o step só é definido quando o agente de fato executa (no ciclo seguinte). O valor correto é `None`.

## Correções aplicadas

### `src/orchestrator/runner.py`

Após o agente concluir, o código agora verifica se a próxima coluna (`_advance`) é um gate humano (sem agente). Se sim, move o card para a coluna de gate. Se não (próxima coluna tem agente, ou não há advance), mantém na coluna atual.

### `tests/test_gate.py`

- **CT-066** (`test_approved_from_human_gate_advances`): corrigida asserção `current_step` para `None`.
- **CT-067** (`test_agent_moves_card_to_human_gate`): novo teste que valida o cenário exato do bug — agente de `analise` finaliza com commit/push/PR e card move para `"Aprovação"`.

## Execução de testes

```
100 passed in 11.50s
```

Nenhuma regressão detectada. Todos os testes existentes continuam passando.

## Casos de teste validados

| CT    | Descrição                                      | Resultado |
|-------|------------------------------------------------|-----------|
| CT-058| pending: nenhuma ação                          | ✅ PASS   |
| CT-059| approved: avança step                          | ✅ PASS   |
| CT-060| rejected: rework=True                          | ✅ PASS   |
| CT-061| rework metrics.record                          | ✅ PASS   |
| CT-062| comentário postado                             | ✅ PASS   |
| CT-063| status awaiting_approval após agente           | ✅ PASS   |
| CT-064| estado persiste                                | ✅ PASS   |
| CT-065| aprovação move para gate humano                | ✅ PASS   |
| CT-066| aprovação no gate humano avança                | ✅ PASS   |
| CT-067| agente move card para gate humano (novo)       | ✅ PASS   |
