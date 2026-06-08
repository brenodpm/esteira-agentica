# Issue #27 — User Stories

Status: draft
Owner: product-agent
Last updated: 2026-06-08

## Inputs
- docs/00-product/issue-27-vision.md
- docs/00-product/issue-27-problem-space.md
- docs/00-product/issue-27-epicos.md
- esteira.yml
- src/orchestrator/runner.py
- src/orchestrator/priority.py
- src/orchestrator/state.py
- src/orchestrator/blocker.py

---

## US-01: State multi-issue

**Épico**: Épico 1 — Refatoração do State para Multi-Issue

**Como** esteira agêntica,
**Quero** manter um state que suporte múltiplas issues ativas simultaneamente,
**Para que** o processamento de uma issue não bloqueie as demais.

### Critérios de Aceitação

1. O `state.json` armazena uma lista de issues ativas (`active_issues`), cada uma com: `issue_number`, `current_feature`, `current_board`, `current_column`, `current_step`, `status`, `rework`.
2. O campo `status` do state raiz indica apenas o estado do ciclo (`running`, `sleeping`), não de uma issue individual.
3. Ao carregar um `state.json` no formato antigo (campos `issue_number`, `current_feature` no nível raiz), o sistema migra automaticamente para o novo formato sem perda de dados.
4. Após migração, o state antigo é preservado em `state.json.bak` (uma única vez).
5. Cada issue ativa tem status independente: `idle`, `running`, `awaiting_approval`, `blocked`.
6. A função `state_mod.load()` sempre retorna o formato novo, independente do formato em disco.

### Fora de escopo
- Persistência em banco de dados (permanece JSON).
- Lock de concorrência (a esteira é single-process).

---

## US-02: Loop multi-board com prioridade

**Épico**: Épico 2 — Loop Multi-Board com Prioridade e Contador

**Como** esteira agêntica,
**Quero** iterar sobre todos os boards ordenados por prioridade em cada ciclo,
**Para que** tarefas de alta prioridade sejam executadas mesmo quando outras estão em gate humano.

### Critérios de Aceitação

1. A cada ciclo, os boards são ordenados por `boards.<id>.priority` (menor valor = maior prioridade).
2. Para cada board, busca-se a próxima tarefa elegível: não bloqueada, não em coluna terminal, ordenada por `createdAt` (mais antiga primeiro).
3. Se a tarefa retornada estiver com status `blocked` ou `awaiting_approval`, ela é ignorada e a busca continua na próxima tarefa do mesmo board.
4. Se nenhuma tarefa elegível existir no board corrente, passa-se ao próximo board na lista.
5. Ao encontrar uma tarefa elegível, o agente correspondente é executado.
6. Após processar uma tarefa (ou não encontrar nenhuma), o loop continua para os demais boards no mesmo ciclo (não retorna imediatamente).
7. O ciclo só termina quando todos os boards foram visitados.

### Fora de escopo
- Execução paralela real (threads/async) — permanece sequencial.

---

## US-03: Contador de execuções e delay inteligente

**Épico**: Épico 2 — Loop Multi-Board com Prioridade e Contador

**Como** esteira agêntica,
**Quero** aplicar delay apenas quando nenhuma tarefa foi executada no ciclo,
**Para que** não haja ociosidade artificial quando há trabalho disponível.

### Critérios de Aceitação

1. No início de cada ciclo, um contador `executions` é inicializado em `0`.
2. A cada execução de agente iniciada com sucesso no ciclo, `executions` é incrementado em `1`.
3. Ao final do ciclo (todos os boards visitados):
   - Se `executions > 0`: inicia novo ciclo imediatamente (sem delay).
   - Se `executions == 0`: aplica delay de `pipe.agent.timeout.sleeptime` minutos (lido do `esteira.yml`) antes de iniciar novo ciclo.
4. O valor de `sleeptime` é lido dinamicamente a cada ciclo (permite hot-reload via edição do yml).
5. O log exibe `[HH:MM:SS] ciclo concluído — X execuções | próximo ciclo: imediato` ou `[HH:MM:SS] ciclo concluído — 0 execuções | próximo ciclo em {sleeptime}s`.

### Fora de escopo
- Backoff exponencial ou adaptativo (usa valor fixo do yml).

---

## US-04: Controle de paralelismo por board

**Épico**: Épico 3 — Controle de Paralelismo por Board

**Como** operador da esteira,
**Quero** que o parâmetro `boards.<id>.parallel` controle quantas tarefas podem estar ativas por vez em um board,
**Para que** boards sensíveis (ex: demanda) não tenham múltiplas execuções simultâneas.

### Critérios de Aceitação

1. Quando `boards.<id>.parallel` = `false`, no máximo uma issue pode ter status diferente de `idle` e `blocked` naquele board.
2. Quando `boards.<id>.parallel` = `true` (ou ausente), não há limite — múltiplas issues podem estar em execução ou `awaiting_approval` simultaneamente no mesmo board.
3. Parâmetro opcional `boards.<id>.max_parallel` (inteiro) permite controle numérico: default `1` quando `parallel: false`, sem limite quando `parallel: true`.
4. Ao buscar tarefa em um board com `parallel: false` e já houver uma issue ativa (running ou awaiting_approval), o board é pulado.
5. A verificação de paralelismo consulta a lista de `active_issues` no state (US-01) filtrando por `current_board`.

### Fora de escopo
- Fila de espera por board (a tarefa simplesmente não é selecionada naquele ciclo).

---

## US-05: Criação automática de débitos — dependência humana

**Épico**: Épico 4 — Mecanismo de Criação de Débitos

**Como** esteira agêntica,
**Quero** criar automaticamente uma issue de débito quando uma tarefa depende de resposta humana,
**Para que** a tarefa original possa ser marcada como bloqueada e a esteira continue processando outras.

### Critérios de Aceitação

1. O board que recebe débitos automáticos é identificado pelo parâmetro `boards.<id>.debt_target: true` no `esteira.yml`.
2. Quando um agente sinaliza dependência humana (via output estruturado ou label `needs-human`), a esteira:
   a. Cria uma issue no board marcado com `debt_target: true`.
   b. O título da issue segue: `[DÉBITO] <descrição da dependência>`.
   c. O body referencia a issue original: `Parent: #<número>`.
   d. A issue original recebe label `blocked`.
3. A issue de débito é criada na coluna `todo` do board de destino (identificada por `boards.<id>.todo`).
4. Se nenhum board tiver `debt_target: true`, a esteira loga um warning e não cria o débito (não falha silenciosamente).

### Fora de escopo
- Resolução automática do débito (será manual ou por agente na coluna do board de débitos).

---

## US-06: Criação automática de débitos — dependência de outro agente

**Épico**: Épico 4 — Mecanismo de Criação de Débitos

**Como** esteira agêntica,
**Quero** criar automaticamente uma issue de débito quando uma tarefa depende de resposta de outro agente,
**Para que** o agente específico possa resolver o débito sem bloquear o fluxo.

### Critérios de Aceitação

1. Quando um agente sinaliza dependência de outro agente (via output estruturado indicando `needs_agent: <nome_agente>`), a esteira:
   a. Cria issue no board com `debt_target: true`.
   b. O body inclui `Parent: #<número>` e `assigned_agent: <nome_agente>`.
   c. A issue original recebe label `blocked`.
2. O campo `assigned_agent` na issue de débito sobrescreve o agente padrão da coluna (`boards.<id>.columns.<col>.agent`) na hora da execução.
3. Parâmetro `boards.<id>.columns.<col>.subscribable_agent: true` indica que aquela coluna permite override de agente por issue. Se a coluna de destino do débito não tiver esse flag, a esteira loga warning mas ainda cria a issue.
4. Na execução da issue de débito, o runner verifica se existe `assigned_agent` no body e usa esse agente ao invés do padrão da coluna.

### Fora de escopo
- Múltiplos agentes assinados na mesma issue.
- Notificação ao agente (o agente é invocado quando a issue chegar na coluna de execução).

---

## US-07: Parametrização completa — sem hardcode

**Épico**: Épico 5 — Parametrização do Delay e Configuração Declarativa

**Como** operador da esteira,
**Quero** que todo comportamento configurável seja derivado de parâmetros explícitos no `esteira.yml`,
**Para que** não existam regras implícitas que dependam de nomes ou valores hardcoded.

### Critérios de Aceitação

1. O delay entre ciclos usa exclusivamente `pipe.agent.timeout.sleeptime` (em minutos).
2. A identificação do board de débitos usa `boards.<id>.debt_target: true` — nenhuma referência hardcoded ao nome "debito" ou "Débitos".
3. O controle de paralelismo usa `boards.<id>.parallel` e `boards.<id>.max_parallel` — sem assumir default por nome de board.
4. A permissão de override de agente usa `boards.<id>.columns.<col>.subscribable_agent: true`.
5. Nenhum board_key, column_id ou board name é usado como identificador funcional no código (ex: `if board_key == "debito"`).
6. Todos os novos parâmetros são documentados com:
   - Nome do parâmetro
   - Tipo
   - Default (quando ausente)
   - Comportamento

### Novos parâmetros no esteira.yml

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `boards.<id>.parallel` | boolean | `true` | Se `false`, limita a 1 issue ativa por vez no board |
| `boards.<id>.max_parallel` | integer | `1` (se parallel=false) / `∞` (se parallel=true) | Limite numérico de issues ativas simultâneas |
| `boards.<id>.debt_target` | boolean | `false` | Indica que este board recebe débitos automáticos |
| `boards.<id>.columns.<col>.subscribable_agent` | boolean | `false` | Permite override do agente padrão por issue |

### Fora de escopo
- Interface gráfica para configuração.
- Validação de schema do yml (pode ser débito futuro).

---

## US-08: Skip de tarefas bloqueadas na seleção

**Épico**: Épico 2 — Loop Multi-Board com Prioridade e Contador

**Como** esteira agêntica,
**Quero** que ao buscar a próxima tarefa, issues bloqueadas sejam ignoradas automaticamente,
**Para que** a esteira nunca fique presa tentando executar uma issue que não pode avançar.

### Critérios de Aceitação

1. Na seleção de tarefa, issues com label `blocked` são excluídas da lista de elegíveis.
2. Issues com status `awaiting_approval` na lista de `active_issues` no state são excluídas da seleção (já estão em processamento).
3. Issues com status `blocked` na lista de `active_issues` no state são excluídas da seleção.
4. A busca continua para a próxima issue elegível no mesmo board antes de avançar ao próximo board.
5. O log registra `[HH:MM:SS] ℹ #<N> ignorada — bloqueada` quando uma issue bloqueada é encontrada durante a varredura.

### Fora de escopo
- Desbloqueio automático baseado em tempo (timeout de bloqueio).

---

## Dependências entre User Stories

```
US-01 (state multi-issue)
 └── US-02 (loop multi-board) — depende de US-01
      ├── US-03 (contador/delay) — depende de US-02
      ├── US-08 (skip bloqueadas) — depende de US-02
      └── US-04 (paralelismo) — depende de US-01 + US-02
US-05 (débito humano) — depende de US-01
US-06 (débito agente) — depende de US-05
US-07 (parametrização) — transversal, evolui com cada US
```

## Ordem de implementação sugerida

1. US-01 → US-02 → US-03 → US-08 (fluxo principal corrigido)
2. US-04 (controle de paralelismo)
3. US-05 → US-06 (mecanismo de débitos)
4. US-07 (validação final de parametrização — transversal)
