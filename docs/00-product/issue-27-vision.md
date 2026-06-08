# Issue #27 — Visão de Produto

## Contexto

A esteira agêntica opera hoje com um **state global singleton**: ao iniciar o processamento de uma issue, todas as demais ficam paradas até que o ciclo daquela issue se encerre (incluindo gates de aprovação humana). Isso significa que, quando uma tarefa avança para "aguardando aprovação", a esteira entra em polling ocioso mesmo havendo dezenas de tarefas prontas em outros boards.

## Problema Observado

A issue #22 avançou corretamente até o gate de aprovação (PR aberto, aguardando code-review humano). A partir desse ponto, a esteira ficou presa indefinidamente em:

```
aguardando aprovação — #22 / quality (próximo ciclo em 300s)
```

…sem executar nenhuma outra tarefa disponível em qualquer board.

## Visão Desejada

A esteira deve se comportar como um **scheduler multi-board orientado a prioridades**, onde:

1. Um ciclo de execução varre **todos os boards ordenados por prioridade** (menor valor numérico = maior prioridade).
2. Dentro de cada board, busca a **próxima tarefa elegível** (não bloqueada, mais antiga).
3. Tarefas em estado de espera (aprovação humana, wait_children) **não travam a esteira** — são simplesmente ignoradas na busca, e a esteira segue para a próxima tarefa ou board.
4. Tarefas que dependam de resposta humana ou de outro agente geram um **débito técnico** no board apropriado, e a tarefa original é marcada como bloqueada.
5. O delay (sleeptime) **só se aplica quando nenhuma tarefa foi executada no ciclo inteiro** — se ao menos uma tarefa foi executada, o próximo ciclo inicia imediatamente.

## Princípios de Design

- **Nenhuma regra hardcoded**: todo comportamento configurável via parâmetros no `esteira.yml`.
- **Parametrização explícita**: se algo precisa ser assumido (ex: "qual board recebe débitos"), deve existir um parâmetro declarativo para isso.
- **Controle de paralelismo por board**: o parâmetro `parallel: false` restringe a execução a no máximo uma tarefa ativa por vez naquele board.
- **Ciclo baseado em contador**: a cada execução de agente, incrementa-se um contador; ao final do ciclo, se contador > 0 → novo ciclo imediato; se contador == 0 → delay.

## Resultado Esperado

- A esteira nunca fica ociosa se há trabalho disponível em qualquer board.
- Gates de aprovação de uma issue não bloqueiam o processamento de issues de outros boards (ou até do mesmo board, se `parallel: true`).
- Débitos técnicos são rastreáveis e atribuíveis a agentes específicos.
- A configuração permanece declarativa e extensível.
