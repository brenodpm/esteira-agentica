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

## Changes (rework v2)
- Reintroduzido suporte a múltiplas issues ativas no state — sem isso o loop multi-board não funciona (se o state é unitário, ao colocar uma issue em `awaiting_approval`, a esteira trava). A solução é trocar o state unitário por uma lista de issues em andamento.
- Removida definição de formato de output estruturado do agente (era suposição técnica) — substituído por contrato genérico: "o agente sinaliza dependência via mecanismo definido na etapa de arquitetura".
- Clarificado que `parallel: false` significa "no máximo 1 tarefa em qualquer estado não-terminal e não-todo no board", impedindo nova seleção.
- Corrigido critério de US-01: a esteira executa no máximo 1 tarefa elegível por board por ciclo, depois avança ao próximo board.
- Adicionada US sobre state multi-issue como pré-requisito estrutural.

---

## US-01: State multi-issue

**Épico**: Épico 1 — Refatoração do State para Multi-Issue

**Como** esteira agêntica,
**Quero** que o state suporte múltiplas issues ativas simultaneamente,
**Para que** o loop possa processar um board mesmo que outro board tenha uma issue aguardando aprovação.

### Comportamento esperado

1. O `state.json` deixa de armazenar uma única issue e passa a conter uma lista de issues ativas (`active_issues`).
2. Cada entrada em `active_issues` contém: `issue_number`, `current_feature`, `current_board`, `current_column`, `current_step`, `status`, `rework`.
3. O campo de nível raiz `status` passa a representar o status geral da esteira (`running`, `idle`), não de uma issue específica.
4. O loop consulta `active_issues` para saber quais issues estão em `awaiting_approval` e quais estão disponíveis para execução.

### Critérios de Aceitação

1. O `state.json` contém um campo `active_issues` (array de objetos).
2. Cada objeto em `active_issues` possui: `issue_number` (int), `current_feature` (string), `current_board` (string), `current_column` (string), `current_step` (string|null), `status` (enum: idle, executing, awaiting_approval), `rework` (bool).
3. Ao carregar um state no formato antigo (unitário), a esteira migra automaticamente para o novo formato sem perda de dados.
4. Quando uma issue entra em `awaiting_approval`, ela permanece em `active_issues` com esse status — não bloqueia a esteira.
5. Quando uma issue é concluída (coluna terminal), ela é removida de `active_issues`.
6. O campo raiz `status` é removido ou passa a ser derivado (`idle` se `active_issues` está vazio ou todas as entries estão em `awaiting_approval`).

### Fora de escopo
- Persistência em banco de dados — permanece em JSON.
- Limpeza automática de entries corrompidas (débito futuro).

---

## US-02: Loop multi-board com prioridade

**Épico**: Épico 2 — Loop Multi-Board com Prioridade e Contador

**Como** esteira agêntica,
**Quero** que cada ciclo percorra todos os boards ordenados por prioridade e execute no máximo uma tarefa elegível por board,
**Para que** a esteira nunca fique ociosa quando há trabalho disponível em qualquer board.

### Comportamento esperado

1. Ordenar boards por `boards.<id>.priority` (menor valor = maior prioridade).
2. Para cada board na ordem:
   a. Verificar restrição de paralelismo (ver US-04). Se board está "cheio", pular para o próximo.
   b. Buscar a próxima tarefa elegível: não bloqueada, não em `awaiting_approval`, ordenada por data de criação (mais antiga primeiro).
   c. Se a tarefa retornada estiver bloqueada ou em `awaiting_approval`, ignorar e buscar a próxima no mesmo board.
   d. Repetir até encontrar tarefa elegível ou esgotar tarefas do board.
   e. Se encontrou tarefa elegível: executar o agente correspondente à coluna da tarefa.
   f. Se não encontrou tarefa elegível: passar ao próximo board.
3. O ciclo termina quando todos os boards foram visitados.

### Critérios de Aceitação

1. Os boards são iterados na ordem de `priority` (menor primeiro) a cada ciclo.
2. Dentro de cada board, as tarefas são ordenadas por `createdAt` ascendente (mais antiga primeiro).
3. Tarefas com label `blocked` são ignoradas na seleção.
4. Tarefas cujo status em `active_issues` é `awaiting_approval` são ignoradas na seleção.
5. Se nenhuma tarefa elegível existe no board, o loop avança ao próximo board sem delay.
6. No máximo 1 tarefa é executada por board por ciclo.
7. O ciclo só termina quando todos os boards foram visitados.
8. O log registra quando uma issue é pulada:
   - `[HH:MM:SS] ℹ #<N> ignorada (bloqueada)`
   - `[HH:MM:SS] ℹ #<N> ignorada (aguardando aprovação)`

### Fora de escopo
- Execução paralela real (threads/async) — permanece sequencial dentro do ciclo.

---

## US-03: Contador de execuções e delay inteligente

**Épico**: Épico 2 — Loop Multi-Board com Prioridade e Contador

**Como** esteira agêntica,
**Quero** aplicar delay apenas quando nenhuma tarefa foi executada no ciclo,
**Para que** não haja ociosidade artificial quando há trabalho disponível.

### Comportamento esperado

1. No início de cada ciclo, inicializar contador `executions = 0`.
2. A cada execução de agente iniciada com sucesso: `executions += 1`.
3. Ao final do ciclo (todos os boards visitados):
   - Se `executions > 0` → iniciar novo ciclo imediatamente.
   - Se `executions == 0` → aplicar delay de `pipe.agent.timeout.sleeptime` (valor em minutos, lido do `esteira.yml`) convertido em segundos.

### Critérios de Aceitação

1. O contador é inicializado em `0` no início de cada ciclo.
2. O contador é incrementado em `1` a cada vez que um agente é invocado com sucesso no ciclo.
3. Se `executions > 0` ao final do ciclo: próximo ciclo inicia imediatamente (delay = 0).
4. Se `executions == 0` ao final do ciclo: delay = `pipe.agent.timeout.sleeptime * 60` segundos.
5. O valor de `sleeptime` é lido do yml a cada ciclo (permite alteração em runtime).
6. O log exibe ao final do ciclo:
   - `[HH:MM:SS] ciclo concluído — N execução(ões) | próximo ciclo: imediato`
   - `[HH:MM:SS] ciclo concluído — 0 execuções | próximo ciclo em Xs`

### Parâmetro utilizado

| Parâmetro | Tipo | Localização | Descrição |
|-----------|------|-------------|-----------|
| `pipe.agent.timeout.sleeptime` | integer (minutos) | esteira.yml | Tempo de espera entre ciclos quando não há trabalho |

### Fora de escopo
- Backoff exponencial ou adaptativo.

---

## US-04: Controle de paralelismo por board

**Épico**: Épico 3 — Controle de Paralelismo por Board

**Como** operador da esteira,
**Quero** que o parâmetro `boards.<id>.parallel` controle se mais de uma tarefa pode estar ativa por vez em um board,
**Para que** boards sensíveis não tenham múltiplas execuções simultâneas.

### Definição de "tarefa ativa"

Uma tarefa é considerada ativa em um board quando:
- Está presente em `active_issues` com `current_board` igual ao board em questão, **E**
- Seu `status` é `executing` ou `awaiting_approval`.

### Critérios de Aceitação

1. Quando `boards.<id>.parallel` = `false` e já existe uma tarefa ativa naquele board, o board é pulado na varredura do ciclo.
2. Quando `boards.<id>.parallel` = `true` (ou ausente — default é `true`), não há restrição de quantidade de tarefas ativas.
3. A verificação de paralelismo ocorre **antes** de buscar tarefas no board. Se o board está "cheio", nem inicia a busca.
4. O log registra `[HH:MM:SS] ℹ board '<id>' pulado (parallel=false, tarefa ativa: #<N>)` quando um board é pulado por esta regra.

### Parâmetro

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `boards.<id>.parallel` | boolean | `true` | Se `false`, limita a 1 tarefa ativa por vez no board |

### Fora de escopo
- Controle numérico fino (`max_parallel`) — pode ser adicionado futuramente se necessário.

---

## US-05: Criação automática de débitos — dependência humana

**Épico**: Épico 4 — Mecanismo de Criação de Débitos

**Como** esteira agêntica,
**Quero** criar automaticamente uma issue de débito quando uma tarefa depende de resposta humana,
**Para que** a tarefa original possa ser marcada como bloqueada e a esteira continue processando outras.

### Critérios de Aceitação

1. O board que recebe débitos automáticos é identificado pelo parâmetro `boards.<id>.debt_target: true`.
2. Quando um agente sinaliza dependência humana (mecanismo de sinalização a ser definido na etapa de arquitetura), a esteira:
   a. Cria uma issue no board com `debt_target: true`, na coluna indicada por `boards.<id>.todo` desse board.
   b. Título da issue: `[DÉBITO] <descrição do motivo>`.
   c. Body contém: `Parent: #<número_issue_original>`.
   d. Adiciona label `needs-human` na issue de débito.
   e. Adiciona label `blocked` na issue original.
   f. A issue original passa a ser ignorada nos próximos ciclos (por estar bloqueada — US-02 critério 3).
3. Se nenhum board tiver `debt_target: true`, a esteira loga warning: `[HH:MM:SS] ⚠ nenhum board com debt_target=true configurado — débito não criado` e a execução continua sem falha.
4. A esteira **não falha** se `debt_target` não estiver configurado — apenas loga e continua.

### Parâmetros

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `boards.<id>.debt_target` | boolean | `false` | Indica que este board recebe débitos automáticos |

### Fora de escopo
- Resolução automática do débito (será manual ou por agente na coluna do board de débitos).
- Definição do formato exato de sinalização do agente (responsabilidade da etapa de arquitetura).

---

## US-06: Criação automática de débitos — dependência de outro agente

**Épico**: Épico 4 — Mecanismo de Criação de Débitos

**Como** esteira agêntica,
**Quero** criar automaticamente uma issue de débito quando uma tarefa depende de resposta de outro agente,
**Para que** o agente específico possa resolver o débito independentemente.

### Critérios de Aceitação

1. Quando um agente sinaliza dependência de outro agente (mecanismo de sinalização a ser definido na etapa de arquitetura, contendo identificação do agente necessário e descrição do motivo), a esteira:
   a. Cria issue no board com `debt_target: true`, na coluna `boards.<id>.todo`.
   b. Título: `[DÉBITO] <descrição>`.
   c. Body contém:
      - `Parent: #<número_issue_original>`
      - `assigned_agent: <nome_agente>`
   d. Adiciona label `blocked` na issue original.
2. Na execução da issue de débito, o runner verifica se o body contém `assigned_agent: <nome>`:
   - Se sim: usa esse agente **ao invés** do agente padrão da coluna.
   - Se não: usa o agente padrão da coluna normalmente.
3. Para que uma coluna aceite override de agente, ela deve ter o parâmetro `boards.<id>.columns.<col>.subscribable_agent: true`. Se a coluna de destino não tiver esse flag, a esteira loga warning mas **ainda cria** a issue de débito (a execução usará o agente padrão).

### Parâmetros

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `boards.<id>.debt_target` | boolean | `false` | Board recebe débitos automáticos |
| `boards.<id>.columns.<col>.subscribable_agent` | boolean | `false` | Coluna permite override do agente padrão por issue |

### Fora de escopo
- Múltiplos agentes assinados na mesma issue.
- Notificação ativa ao agente (o agente é invocado quando a issue chegar na sua vez de execução).

---

## US-07: Verificação de gates humanos no ciclo

**Épico**: Épico 2 — Loop Multi-Board com Prioridade e Contador

**Como** esteira agêntica,
**Quero** verificar o status de aprovação de todas as issues em `awaiting_approval` a cada ciclo,
**Para que** issues aprovadas ou rejeitadas sejam processadas no mesmo ciclo sem esperar.

### Critérios de Aceitação

1. No início de cada ciclo, antes de varrer boards para novas tarefas, a esteira itera sobre todas as entries em `active_issues` com `status == awaiting_approval`.
2. Para cada uma, consulta o status de aprovação:
   - `approved` → avança a issue para a próxima coluna (remove `approved` label, faz merge se aplicável, atualiza entry).
   - `rejected` → marca `rework: true` e `status: idle` na entry (será re-selecionada no ciclo).
   - `pending` → mantém como está.
3. Aprovações processadas contam para o contador de execuções (`executions += 1`) se resultaram em avanço para coluna com agente.
4. O log registra cada aprovação/rejeição processada.

### Fora de escopo
- Timeout automático de gates (se o humano nunca responder, a issue permanece em `awaiting_approval` indefinidamente).

---

## US-08: Parametrização completa — sem hardcode

**Épico**: Épico 5 — Parametrização do Delay e Configuração Declarativa

**Como** operador da esteira,
**Quero** que todo comportamento configurável seja derivado de parâmetros explícitos no `esteira.yml`,
**Para que** não existam regras implícitas que dependam de nomes ou valores fixos no código.

### Critérios de Aceitação

1. O delay entre ciclos usa exclusivamente `pipe.agent.timeout.sleeptime` (em minutos).
2. A identificação do board de débitos usa `boards.<id>.debt_target: true` — nenhuma referência hardcoded a nomes como "debito" ou "Débitos".
3. O controle de paralelismo usa `boards.<id>.parallel` — sem assumir default por nome de board.
4. A permissão de override de agente usa `boards.<id>.columns.<col>.subscribable_agent: true`.
5. A coluna de entrada para novas issues usa `boards.<id>.todo` — sem assumir "backlog".
6. Nenhum `board_key`, `column_id` ou `board.name` é usado como identificador funcional no código (ex: proibido `if board_key == "debito"`).
7. Todos os parâmetros são documentados no artefato.

### Tabela completa de parâmetros

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `pipe.agent.timeout.sleeptime` | integer | — | Minutos de delay entre ciclos ociosos |
| `boards.<id>.priority` | integer | `0` | Prioridade do board (menor = mais prioritário) |
| `boards.<id>.parallel` | boolean | `true` | Se `false`, limita a 1 tarefa ativa por vez |
| `boards.<id>.debt_target` | boolean | `false` | Board recebe débitos automáticos |
| `boards.<id>.todo` | string | — | Coluna de entrada (onde issues novas/débitos são criados) |
| `boards.<id>.columns.<col>.subscribable_agent` | boolean | `false` | Permite override do agente padrão por issue |

### Fora de escopo
- Interface gráfica para configuração.
- Validação de schema do yml (débito futuro).

---

## Dependências entre User Stories

```
US-01 (state multi-issue)
 └── US-02 (loop multi-board) — depende de US-01
      ├── US-03 (contador/delay) — depende de US-02
      ├── US-04 (paralelismo) — depende de US-02
      └── US-07 (gates no ciclo) — depende de US-01 + US-02
US-05 (débito humano) — depende de US-02
US-06 (débito agente) — depende de US-05
US-08 (parametrização) — transversal, evolui com cada US
```

## Ordem de implementação sugerida

1. **US-01** → State multi-issue (pré-requisito estrutural)
2. **US-02** → Loop multi-board (resolve o problema principal: esteira travada)
3. **US-07** → Verificação de gates no ciclo (completa o loop)
4. **US-03** → Contador e delay inteligente (complemento de US-02)
5. **US-04** → Controle de paralelismo (restrição sobre US-02)
6. **US-05** → Débitos por dependência humana
7. **US-06** → Débitos por dependência de agente
8. **US-08** → Validação final de parametrização (transversal)

---

## Glossário

| Termo | Definição |
|-------|-----------|
| Ciclo | Uma iteração completa sobre todos os boards |
| Tarefa elegível | Issue não bloqueada, não em awaiting_approval, não em coluna terminal |
| Board ativo | Board que possui ao menos uma tarefa elegível |
| Tarefa ativa | Issue em active_issues com status executing ou awaiting_approval para aquele board |
| debt_target | Flag que identifica o board receptor de débitos automáticos |
| subscribable_agent | Flag que permite override do agente padrão numa coluna |
| active_issues | Lista no state.json com todas as issues sendo acompanhadas pela esteira |
