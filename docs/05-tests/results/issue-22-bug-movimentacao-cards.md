# Resultado de Testes — Issue #22: Movimentação incorreta dos cards no board

**Data:** 2026-06-06  
**Etapa:** quality / reteste  
**Agente:** quality  
**Ação:** Reexecutar casos de teste e validar que o bug foi corrigido sem regressão

---

## Diagnóstico do Bug

Após o agente executar em uma coluna com `agent` + `git_commit`, ao receber aprovação o runner
avançava para a próxima coluna mas definia `current_step = None`. Isso causava dois problemas:

1. **Movimentação do card**: ao avançar para uma coluna de gate humano (sem agente), o
   `move_card` era chamado corretamente — mas o `current_step = None` fazia o display ficar
   `"aguardando aprovação — #N / None"`, e o log do gate usava `"unknown"` como step.

2. **Caso específico reportado**: após a coluna `analise-negocio` criar o PR e receber
   `approved`, deveria mover para `aprovacao-negocio` (gate humano). O runner fazia o move
   corretamente, mas o state ficava inconsistente com `current_step = None` em vez do agente
   esperado.

### Causa raiz

No `src/orchestrator/runner.py`, no bloco de tratamento de `approved`, ao avançar para uma
coluna com agente (`next_has_agent`), o código sempre definia `current_step = None`:

```python
# ANTES (bugado)
if next_col_id and (next_has_agent or next_is_wait):
    current_state["current_column"] = next_col_id
    current_state["current_step"] = None   # ← perdia o agente da próxima coluna
    current_state["status"] = "idle"
```

---

## Correção Aplicada

**Arquivo:** `src/orchestrator/runner.py`

```python
# DEPOIS (corrigido)
if next_col_id and (next_has_agent or next_is_wait):
    current_state["current_column"] = next_col_id
    current_state["current_step"] = next_has_agent or None  # preserva agente da próxima coluna
    current_state["status"] = "idle"
```

`next_has_agent` contém o nome do agente da próxima coluna (string truthy) ou `False`/`None`.
O operador `or None` garante que `wait_children` (sem agente) ainda resulte em `None`.

---

## Casos de Teste Executados

| ID      | Descrição                                                                 | Resultado |
|---------|---------------------------------------------------------------------------|-----------|
| CT-058  | pending: nenhuma ação, estado inalterado                                  | ✅ PASS   |
| CT-059  | approved: avança para próxima coluna com agente, current_step preenchido  | ✅ PASS   |
| CT-060  | rejected: current_step mantido, rework=True                               | ✅ PASS   |
| CT-061  | re-execução com rework=True registra metrics com rework=True              | ✅ PASS   |
| CT-062  | comentário pontual postado após execução do agente                        | ✅ PASS   |
| CT-063  | estado salvo com status="awaiting_approval" após agente                   | ✅ PASS   |
| CT-064  | estado "awaiting_approval" persiste após reinicialização                  | ✅ PASS   |
| CT-065  | approved em coluna com agente → próxima é gate humano: move card          | ✅ PASS   |
| CT-066  | approved no gate humano → avança para coluna com agente, status=idle      | ✅ PASS   |

---

## Suite Completa

```
99 passed in 3.90s
```

Nenhuma regressão detectada. Todos os 99 testes passando.

---

## Observação sobre o Comportamento em Produção

O log de 2026-06-06 mostrou que o agente moveu corretamente o card de `Backlog` para
`Análise de negócio` e criou o PR. A movimentação para `Aprovação de Negócio` não ocorreu
automaticamente porque, naquele ciclo, o `current_step` ficou `None` após o approve ser
processado — impedindo o display e o rastreamento correto do próximo passo. Com a correção,
o state reflete o agente da próxima coluna assim que a aprovação é processada.
