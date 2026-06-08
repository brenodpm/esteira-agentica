# Issue #27 — Problem Space

## Problema Raiz

A arquitetura atual do runner (`src/orchestrator/runner.py`) utiliza um **state unitário persistido em `state.json`** que armazena exatamente uma issue ativa. A função `run_once()` opera em modo exclusivo:

- Se o state está em `awaiting_approval`, o ciclo inteiro retorna sem fazer nada.
- Se o state está em `idle` com uma `current_feature`, executa apenas aquela issue.
- Não existe iteração sobre múltiplos boards no mesmo ciclo.

### Consequências Diretas

1. **Esteira travada em gates humanos**: qualquer issue que chega a um gate de aprovação paralisa toda a esteira até aprovação/rejeição.
2. **Inversão de prioridade**: tarefas de alta prioridade (bugs, priority 0) ficam paradas enquanto uma task de menor prioridade aguarda code-review.
3. **Ociosidade artificial**: o delay (sleeptime) é aplicado incondicionalmente a cada ciclo, mesmo quando há trabalho disponível.
4. **Ausência de mecanismo de débito**: quando um agente precisa de input humano ou de outro agente, não há caminho para criar um débito e desbloquear a tarefa original automaticamente.
5. **Regra `parallel: false` não implementada**: não existe verificação de quantas tarefas estão ativas em um board para respeitar a configuração.

### Impacto no Fluxo

```
Ciclo N: executa #22 (quality) → PR aberto → state = awaiting_approval
Ciclo N+1: detecta awaiting_approval → verifica aprovação → pending → RETURN
Ciclo N+2: mesmo → RETURN
...
(Bugs e tasks de alta prioridade permanecem parados indefinidamente)
```

## Restrições

- O state precisa suportar múltiplas issues em andamento simultaneamente (uma por board se `parallel: false`, ou N se `parallel: true`).
- A parametrização não pode assumir nomes de boards hardcoded — deve-se usar atributos declarativos (ex: `debt_target: true` para indicar o board que recebe débitos).
- O mecanismo de criação de débitos precisa permitir subscrição de agente específico para resolver o débito (overriding o agente padrão da coluna do board de destino).
- A esteira deve continuar single-process (sem threading), operando em loop sequencial — o "paralelismo" é lógico (múltiplas issues em diferentes estados), não de execução.

## Perguntas-Chave para Solução

1. Como representar no state múltiplas issues ativas sem conflito?
2. Como determinar se um board permite nova execução (respeitando `parallel`)?
3. Como identificar o board-alvo para débitos via configuração?
4. Como associar um agente específico a uma issue de débito?
5. Qual a estrutura do contador de execuções por ciclo?
