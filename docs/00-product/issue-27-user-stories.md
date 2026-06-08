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

## Changes (rework)
- Removida US-01 (state multi-issue) — complexidade desnecessária. O problema é o loop travar em `awaiting_approval`, não a estrutura do state. A solução é o loop ignorar issues em espera e buscar outra.
- Reescrita US-02 para refletir fielmente o comportamento descrito passo-a-passo pelo usuário.
- Simplificada US-04 (paralelismo) — removido `max_parallel`, mantido apenas `parallel: false/true` conforme solicitado.
- Corrigida sequência lógica: o loop agora trata `awaiting_approval` como estado da issue (não da esteira inteira).
- Adicionada parametrização `boards.<id>.todo` como coluna de entrada para débitos criados.

---

## US-01: Loop multi-board com prioridade

**Épico**: Épico 2 — Loop Multi-Board com Prioridade e Contador

**Como** esteira agêntica,
**Quero** que cada ciclo percorra todos os boards ordenados por prioridade e busque a próxima tarefa elegível em cada um,
**Para que** a esteira nunca fique ociosa quando há trabalho disponível em qualquer board.

### Comportamento esperado

1. Ordenar boards por `boards.<id>.priority` (menor valor = maior prioridade).
2. Para cada board na ordem:
   a. Buscar a próxima tarefa sem bloqueio, ordenada por data de criação (mais antiga primeiro).
   b. Se a tarefa retornada estiver bloqueada (`blocked`) ou em `awaiting_approval`, ignorar e buscar a próxima tarefa no mesmo board.
   c. Repetir até encontrar uma tarefa elegível ou esgotar as tarefas do board.
   d. Se encontrou tarefa elegível: executar o agente correspondente à coluna da tarefa.
   e. Se não encontrou nenhuma tarefa elegível no board: passar ao próximo board na lista.
3. O ciclo termina quando todos os boards foram visitados.

### Critérios de Aceitação

1. Os boards são iterados na ordem de `priority` (menor primeiro) a cada ciclo.
2. Dentro de cada board, as tarefas são ordenadas por `createdAt` ascendente (mais antiga primeiro).
3. Tarefas com label `blocked` são ignoradas na seleção.
4. Tarefas em estado `awaiting_approval` (aguardando gate humano) são ignoradas na seleção.
5. Se nenhuma tarefa elegível existe no board corrente, o loop avança ao próximo board sem delay.
6. Ao encontrar tarefa elegível, o agente da coluna é executado e o loop continua para os demais boards (não retorna imediatamente).
7. O ciclo só termina quando todos os boards foram visitados.
8. O log registra `[HH:MM:SS] ℹ #<N> ignorada (bloqueada)` ou `[HH:MM:SS] ℹ #<N> ignorada (aguardando aprovação)` quando uma issue é pulada.

### Impacto no código

- `run_once()` deixa de operar em modo singleton. O status `awaiting_approval` passa a ser da **issue** (persistido por issue), não da esteira.
- `select_next()` passa a ser chamado **por board**, e não globalmente.

### Fora de escopo
- Execução paralela real (threads/async) — permanece sequencial dentro do ciclo.

---

## US-02: Contador de execuções e delay inteligente

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

## US-03: Controle de paralelismo por board

**Épico**: Épico 3 — Controle de Paralelismo por Board

**Como** operador da esteira,
**Quero** que o parâmetro `boards.<id>.parallel` controle se mais de uma tarefa pode estar ativa por vez em um board,
**Para que** boards sensíveis não tenham múltiplas execuções simultâneas.

### Regra

> Se `boards.<id>.parallel` for igual a `false`, apenas uma tarefa pode estar ativa por vez naquele board.

### Critérios de Aceitação

1. Quando `boards.<id>.parallel` = `false` e já existe uma tarefa ativa (em execução ou `awaiting_approval`) naquele board, o board é pulado na varredura do ciclo.
2. Quando `boards.<id>.parallel` = `true` (ou ausente — default é `true`), não há restrição de quantidade de tarefas ativas.
3. "Tarefa ativa" significa: issue cujo status no contexto daquele board é diferente de `idle`, `blocked`, ou coluna terminal.
4. A verificação de paralelismo ocorre **antes** de buscar tarefas no board. Se o board está "cheio", nem inicia a busca.
5. O log registra `[HH:MM:SS] ℹ board '<nome>' pulado (parallel=false, tarefa ativa: #<N>)` quando um board é pulado por esta regra.

### Parâmetro

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `boards.<id>.parallel` | boolean | `true` | Se `false`, limita a 1 tarefa ativa por vez no board |

### Fora de escopo
- Controle numérico fino (`max_parallel`) — pode ser adicionado futuramente se necessário.

---

## US-04: Criação automática de débitos — dependência humana

**Épico**: Épico 4 — Mecanismo de Criação de Débitos

**Como** esteira agêntica,
**Quero** criar automaticamente uma issue de débito quando uma tarefa depende de resposta humana,
**Para que** a tarefa original possa ser marcada como bloqueada e a esteira continue processando outras.

### Critérios de Aceitação

1. O board que recebe débitos automáticos é identificado pelo parâmetro `boards.<id>.debt_target: true`.
2. Quando um agente sinaliza dependência humana (via output estruturado contendo `needs_human: true` e `description: "<motivo>"`), a esteira:
   a. Cria uma issue no board com `debt_target: true`, na coluna indicada por `boards.<id>.todo` desse board.
   b. Título da issue: `[DÉBITO] <description do output>`.
   c. Body contém: `Parent: #<número_issue_original>`.
   d. Adiciona label `needs-human` na issue de débito.
   e. Adiciona label `blocked` na issue original.
   f. A issue original passa a ser ignorada nos próximos ciclos (por estar bloqueada — US-01 critério 3).
3. Se nenhum board tiver `debt_target: true`, a esteira loga warning: `[HH:MM:SS] ⚠ nenhum board com debt_target=true configurado — débito não criado`.
4. A esteira **não falha** se `debt_target` não estiver configurado — apenas loga e continua.

### Parâmetros

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `boards.<id>.debt_target` | boolean | `false` | Indica que este board recebe débitos automáticos |

### Fora de escopo
- Resolução automática do débito (será manual ou por agente na coluna do board de débitos).

---

## US-05: Criação automática de débitos — dependência de outro agente

**Épico**: Épico 4 — Mecanismo de Criação de Débitos

**Como** esteira agêntica,
**Quero** criar automaticamente uma issue de débito quando uma tarefa depende de resposta de outro agente,
**Para que** o agente específico possa resolver o débito independentemente.

### Critérios de Aceitação

1. Quando um agente sinaliza dependência de outro agente (via output estruturado contendo `needs_agent: "<nome_agente>"` e `description: "<motivo>"`), a esteira:
   a. Cria issue no board com `debt_target: true`, na coluna `boards.<id>.todo`.
   b. Título: `[DÉBITO] <description>`.
   c. Body contém:
      - `Parent: #<número_issue_original>`
      - `assigned_agent: <nome_agente>`
   d. Adiciona label `blocked` na issue original.
2. Na execução da issue de débito, o runner verifica se o body contém `assigned_agent: <nome>`:
   - Se sim: usa esse agente **ao invés** do agente padrão da coluna.
   - Se não: usa o agente padrão da coluna normalmente.
3. Para que uma coluna aceite override de agente, ela deve ter o parâmetro `subscribable_agent: true`. Se a coluna de destino não tiver esse flag, a esteira loga warning mas **ainda cria** a issue de débito (a execução usará o agente padrão).

### Parâmetros

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `boards.<id>.debt_target` | boolean | `false` | Board recebe débitos automáticos |
| `boards.<id>.columns.<col>.subscribable_agent` | boolean | `false` | Coluna permite override do agente padrão por issue |

### Fora de escopo
- Múltiplos agentes assinados na mesma issue.
- Notificação ativa ao agente (o agente é invocado quando a issue chegar na sua vez de execução).

---

## US-06: Parametrização completa — sem hardcode

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
US-01 (loop multi-board)
 ├── US-02 (contador/delay) — depende de US-01
 └── US-03 (paralelismo) — depende de US-01
US-04 (débito humano) — independente (pode ser paralelo)
US-05 (débito agente) — depende de US-04
US-06 (parametrização) — transversal, evolui com cada US
```

## Ordem de implementação sugerida

1. **US-01** → Loop multi-board (resolve o problema principal: esteira travada)
2. **US-02** → Contador e delay inteligente (complemento direto de US-01)
3. **US-03** → Controle de paralelismo (restrição sobre US-01)
4. **US-04** → Débitos por dependência humana
5. **US-05** → Débitos por dependência de agente
6. **US-06** → Validação final de parametrização (transversal, evolui com cada US)

---

## Glossário

| Termo | Definição |
|-------|-----------|
| Ciclo | Uma iteração completa sobre todos os boards |
| Tarefa elegível | Issue não bloqueada, não em awaiting_approval, não em coluna terminal |
| Board ativo | Board que possui ao menos uma tarefa elegível |
| Tarefa ativa | Issue em execução ou awaiting_approval em um board |
| debt_target | Flag que identifica o board receptor de débitos automáticos |
| subscribable_agent | Flag que permite override do agente padrão numa coluna |
