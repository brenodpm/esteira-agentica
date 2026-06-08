# Issue #27 — User Stories

Status: draft
Owner: product-agent
Last updated: 2026-06-08

## Inputs
- docs/00-product/issue-27-vision.md
- docs/00-product/issue-27-problem-space.md
- docs/00-product/issue-27-epicos.md
- esteira.yml
- src/orchestrator/runner.py (código atual — state singleton)
- src/orchestrator/state.py
- src/orchestrator/priority.py
- src/orchestrator/blocker.py

## Changes (rework v4)
- Adicionada **US-09**: Desbloqueio automático ao concluir issue-filha de débito — estava mencionada no v3 mas não materializada.
- **US-01** reescrita: foco no comportamento observável do ciclo multi-board, explicitando que a esteira deve processar **múltiplas issues em paralelo lógico** (não ficar presa a uma só).
- **US-02** expandida: critério explícito para "se a tarefa retornada está bloqueada, buscar a próxima" (passo 4 do usuário).
- **US-03** clarificada: definição precisa de "tarefa ativa" incluindo issues em gate de aprovação no board.
- **US-05/US-06**: adicionado contrato de sinalização — como o agente comunica a dependência para a esteira (via exit code ou marcador no output).
- **US-07** reformulada: gates são verificados **dentro da varredura de cada board**, não como passo separado — alinhado com o loop descrito pelo usuário.
- Removido Épico 1 das referências (decisão de state é arquitetura).
- Todos os parâmetros consolidados em US-08 com defaults explícitos.

---

## US-01: Ciclo de varredura multi-board por prioridade

**Épico**: Épico 2 — Loop Multi-Board com Prioridade e Contador

**Como** esteira agêntica,
**Quero** que cada ciclo percorra todos os boards na ordem de prioridade (menor valor primeiro) e possa executar tarefas de diferentes boards no mesmo ciclo,
**Para que** a esteira nunca fique ociosa enquanto há trabalho disponível em qualquer board.

### Comportamento esperado

1. No início do ciclo, listar todos os boards configurados em `esteira.yml`.
2. Ordenar pela propriedade `boards.<id>.priority` — menor valor = maior prioridade.
3. Percorrer a lista sequencialmente. Para cada board, aplicar as regras de seleção de tarefa (US-02).
4. Se uma tarefa é executada num board, avançar ao **próximo board** na lista (não reiniciar).
5. Após visitar todos os boards, o ciclo se encerra.
6. A esteira **não depende de state singleton** — se uma issue está em gate de aprovação, ela é simplesmente ignorada e o ciclo continua buscando outras tarefas.

### Critérios de Aceitação

| # | Critério |
|---|----------|
| 1 | Os boards são iterados na ordem crescente de `boards.<id>.priority`. |
| 2 | Todos os boards configurados são visitados em cada ciclo. |
| 3 | Se dois boards têm a mesma prioridade, a ordem é determinística (alfabética pelo identificador). |
| 4 | Uma issue em gate de aprovação (aguardando humano) **não impede** execução de outras issues em outros boards. |
| 5 | Uma issue em gate de aprovação no **mesmo board** com `parallel: true` não impede execução de outra issue desse board. |
| 6 | Log no início do ciclo: `[HH:MM:SS] ciclo iniciado — boards: <lista ordenada>`. |

### Parâmetro

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `boards.<id>.priority` | integer | `0` | Prioridade do board (menor = mais prioritário) |

---

## US-02: Seleção de próxima tarefa elegível no board

**Épico**: Épico 2 — Loop Multi-Board com Prioridade e Contador

**Como** esteira agêntica,
**Quero** selecionar a próxima tarefa elegível dentro de um board (não bloqueada, mais antiga primeiro) e, se a primeira estiver impedida, buscar a próxima,
**Para que** o processamento respeite a ordem cronológica e não pare por causa de uma tarefa individual impedida.

### Comportamento esperado

1. Dentro de um board, listar tarefas em colunas que possuem `agent` (colunas executáveis).
2. Ordenar por data de criação ascendente (mais antiga primeiro).
3. Ignorar tarefas que possuam label `blocked`.
4. Ignorar tarefas que estejam em coluna de gate humano (`git_merge: true` sem `agent`, ou com `wait_children: true`).
5. **Se a primeira tarefa da lista filtrada está impedida por qualquer motivo (bloqueada, gate, etc.), pular para a próxima** — iterar até encontrar uma elegível ou esgotar a lista.
6. Se nenhuma tarefa elegível existe no board, passar ao próximo board.

### Critérios de Aceitação

| # | Critério |
|---|----------|
| 1 | Tarefas são ordenadas por `createdAt` ascendente. |
| 2 | Tarefas com label `blocked` são excluídas. |
| 3 | Tarefas em colunas sem `agent` (gates, terminais, wait_children) são excluídas da seleção de execução. |
| 4 | Se a primeira tarefa está impedida, a esteira tenta a próxima — não para. |
| 5 | Se nenhuma tarefa elegível existe, o loop avança ao próximo board sem delay. |
| 6 | Log para cada issue ignorada: `[HH:MM:SS] ℹ #<N> ignorada (<motivo>)`. Motivos: `bloqueada`, `aguardando aprovação`, `aguardando filhos`. |
| 7 | A tarefa selecionada é a mais antiga entre as elegíveis. |

---

## US-03: Controle de paralelismo por board

**Épico**: Épico 3 — Controle de Paralelismo por Board

**Como** operador da esteira,
**Quero** que `boards.<id>.parallel: false` impeça que mais de uma tarefa esteja ativa por vez naquele board,
**Para que** boards sensíveis não tenham execuções concorrentes.

### Definição de "tarefa ativa"

Uma tarefa está **ativa** naquele board quando:
- Está em execução por um agente neste ciclo, **OU**
- Está aguardando aprovação humana (coluna de gate com `git_merge: true`, sem `agent`), **OU**
- Está aguardando filhos (`wait_children: true`)

### Comportamento esperado

1. Antes de selecionar tarefas no board, verificar se `parallel` é `false`.
2. Se `parallel: false` e já existe **uma tarefa ativa** naquele board → pular o board inteiro.
3. Se `parallel: true` (ou ausente — default `true`) → sem restrição, múltiplas issues podem estar em andamento.

### Critérios de Aceitação

| # | Critério |
|---|----------|
| 1 | Board com `parallel: false` e tarefa ativa é pulado. |
| 2 | Default de `parallel` é `true` quando não declarado. |
| 3 | Issue em gate de aprovação **conta como ativa** para fins de paralelismo. |
| 4 | Issue em `wait_children` **conta como ativa** para fins de paralelismo. |
| 5 | Log: `[HH:MM:SS] ℹ board '<id>' pulado (parallel=false, tarefa ativa: #<N>)`. |

### Parâmetro

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `boards.<id>.parallel` | boolean | `true` | Se `false`, no máximo 1 tarefa ativa por vez |

---

## US-04: Contador de execuções e delay inteligente

**Épico**: Épico 2 — Loop Multi-Board com Prioridade e Contador

**Como** esteira agêntica,
**Quero** aplicar delay apenas quando nenhuma tarefa foi executada no ciclo,
**Para que** não haja ociosidade quando há trabalho disponível.

### Comportamento esperado

1. No início do ciclo, inicializar `executions = 0`.
2. A cada execução de agente **iniciada**: `executions += 1`.
3. Ao final do ciclo:
   - Se `executions > 0` → novo ciclo imediatamente (delay = 0).
   - Se `executions == 0` → delay de `pipe.agent.timeout.sleeptime` minutos antes do próximo ciclo.

### Critérios de Aceitação

| # | Critério |
|---|----------|
| 1 | Contador inicializado em `0` a cada ciclo. |
| 2 | Incrementado em `1` a cada agente invocado (antes do resultado). |
| 3 | `executions > 0` ao final → próximo ciclo sem delay. |
| 4 | `executions == 0` ao final → delay = `pipe.agent.timeout.sleeptime × 60` segundos. |
| 5 | Valor de `sleeptime` relido do yml a cada ciclo (permite hot-reload). |
| 6 | Log ao final: `[HH:MM:SS] ciclo concluído — N execução(ões) | próximo ciclo: imediato` ou `[HH:MM:SS] ciclo concluído — 0 execuções | próximo ciclo em Xs`. |

### Parâmetro

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `pipe.agent.timeout.sleeptime` | integer (minutos) | Delay entre ciclos ociosos |

---

## US-05: Criação de débito por dependência humana

**Épico**: Épico 4 — Mecanismo de Criação de Débitos

**Como** esteira agêntica,
**Quero** criar automaticamente uma issue de débito quando um agente sinaliza que precisa de resposta humana,
**Para que** a tarefa original seja bloqueada e a esteira continue processando outras tarefas.

### Contrato de sinalização

O agente sinaliza dependência humana incluindo no **output** um bloco estruturado:

```
<!-- debt:human
reason: <descrição do que precisa do humano>
-->
```

A esteira detecta esse marcador no output do agente após a execução.

### Comportamento esperado

1. Após execução do agente, a esteira verifica se o output contém o marcador `<!-- debt:human ... -->`.
2. Se presente:
   a. Identifica o board com `debt_target: true`.
   b. Cria issue nesse board, na coluna `boards.<id>.todo`.
   c. Marca a issue original com label `blocked`.
   d. A issue original referencia a issue de débito no body.
3. Se não presente: segue fluxo normal.

### Critérios de Aceitação

| # | Critério |
|---|----------|
| 1 | Issue de débito criada no board com `debt_target: true`, na coluna `boards.<id>.todo`. |
| 2 | Título: `[DÉBITO] <reason extraída do marcador>`. |
| 3 | Body contém: `parent: #<número_issue_original>`. |
| 4 | Label `needs-human` adicionada na issue de débito. |
| 5 | Label `blocked` adicionada na issue original. |
| 6 | Se nenhum board tem `debt_target: true`: log warning `[HH:MM:SS] ⚠ nenhum board com debt_target=true — débito não criado` e a esteira **não falha**. |
| 7 | A issue original é ignorada nos próximos ciclos (US-02, critério 2). |
| 8 | O commit/push/PR do agente ocorre normalmente antes da criação do débito (o trabalho parcial é preservado). |

### Parâmetros

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `boards.<id>.debt_target` | boolean | `false` | Board receptor de débitos automáticos |
| `boards.<id>.todo` | string | — | Coluna de entrada para novas issues |

---

## US-06: Criação de débito por dependência de outro agente

**Épico**: Épico 4 — Mecanismo de Criação de Débitos

**Como** esteira agêntica,
**Quero** criar issue de débito com agente específico atribuído quando um agente sinaliza que depende de outro agente,
**Para que** o débito seja resolvido pelo agente correto, não pelo agente padrão da coluna.

### Contrato de sinalização

O agente sinaliza dependência de outro agente incluindo no output:

```
<!-- debt:agent
reason: <descrição do que é necessário>
agent: <nome do agente que deve resolver>
-->
```

### Comportamento esperado

1. Após execução do agente, verificar marcador `<!-- debt:agent ... -->`.
2. Se presente:
   a. Criar issue de débito no board com `debt_target: true`.
   b. Body contém `assigned_agent: <nome>` e `parent: #<número_original>`.
   c. Marcar issue original com label `blocked`.
3. Na execução futura da issue de débito: se body contém `assigned_agent` **e** a coluna de destino tem `subscribable_agent: true` → usar o agente indicado ao invés do padrão da coluna.

### Critérios de Aceitação

| # | Critério |
|---|----------|
| 1 | Issue de débito criada com `assigned_agent: <nome>` no body. |
| 2 | Label `blocked` adicionada na issue original. |
| 3 | Body contém `parent: #<número_issue_original>`. |
| 4 | Na execução: se body tem `assigned_agent` e coluna tem `subscribable_agent: true` → usa agente indicado. |
| 5 | Se coluna **não** tem `subscribable_agent: true` → log warning e usa agente padrão da coluna. |
| 6 | A esteira **não falha** em nenhum cenário de configuração ausente ou inválida. |
| 7 | Label `needs-agent` adicionada na issue de débito (diferencia de `needs-human`). |

### Parâmetros

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `boards.<id>.debt_target` | boolean | `false` | Board receptor de débitos |
| `boards.<id>.columns.<col>.subscribable_agent` | boolean | `false` | Coluna permite override de agente por issue |

---

## US-07: Processamento de gates de aprovação durante varredura

**Épico**: Épico 2 — Loop Multi-Board com Prioridade e Contador

**Como** esteira agêntica,
**Quero** verificar e processar aprovações/rejeições pendentes durante a varredura de cada board,
**Para que** issues aprovadas avancem sem esperar um ciclo extra.

### Comportamento esperado

1. Durante a varredura de um board, **antes de selecionar novas tarefas**, verificar se há issues em colunas de gate (`git_merge: true`, sem `agent`) com status de aprovação resolvido.
2. Para cada issue em gate:
   - Se **aprovada**: executar merge, mover para próxima coluna.
   - Se **rejeitada**: mover para coluna indicada em `change.reprovar` (rework).
   - Se **pendente**: não fazer nada (issue continua no gate).
3. Se a aprovação resultar em avanço para coluna com `agent`, essa issue se torna elegível para execução no mesmo ciclo.

### Critérios de Aceitação

| # | Critério |
|---|----------|
| 1 | Gates são verificados em cada board durante a varredura. |
| 2 | Aprovação → merge do PR + avanço para próxima coluna. |
| 3 | Rejeição → move para coluna `change.reprovar` com flag de rework. |
| 4 | Pendente → issue permanece no gate, é ignorada na seleção. |
| 5 | Avanço para coluna com agente após aprovação **conta** para o contador de execuções (se o agente for executado neste ciclo). |
| 6 | Log: `[HH:MM:SS] ✓ #<N> aprovada — avançando para '<coluna>'` ou `[HH:MM:SS] ↩ #<N> rejeitada — retornando para '<coluna>'`. |

---

## US-08: Parametrização completa — sem hardcode

**Épico**: Épico 5 — Parametrização do Delay e Configuração Declarativa

**Como** operador da esteira,
**Quero** que todo comportamento configurável derive de parâmetros explícitos no `esteira.yml`,
**Para que** não existam regras implícitas ou valores fixos no código.

### Critérios de Aceitação

| # | Critério |
|---|----------|
| 1 | Delay usa `pipe.agent.timeout.sleeptime`. |
| 2 | Board de débitos identificado exclusivamente por `boards.<id>.debt_target: true`. |
| 3 | Paralelismo usa `boards.<id>.parallel`. |
| 4 | Override de agente usa `boards.<id>.columns.<col>.subscribable_agent: true`. |
| 5 | Coluna de entrada de débitos usa `boards.<id>.todo` do board com `debt_target: true`. |
| 6 | Proibido no código: qualquer referência funcional por nome/key de board (ex: `if board == "debito"`). |
| 7 | Labels usadas pelo mecanismo de bloqueio configuráveis via parâmetro `pipe.labels.blocked` (default: `blocked`). |
| 8 | Labels de débito humano/agente configuráveis via `pipe.labels.needs_human` / `pipe.labels.needs_agent`. |

### Tabela consolidada de parâmetros

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `pipe.agent.timeout.sleeptime` | integer | — | Minutos de delay entre ciclos ociosos |
| `pipe.labels.blocked` | string | `blocked` | Label que indica issue bloqueada |
| `pipe.labels.needs_human` | string | `needs-human` | Label para débitos que precisam de humano |
| `pipe.labels.needs_agent` | string | `needs-agent` | Label para débitos que precisam de outro agente |
| `boards.<id>.priority` | integer | `0` | Prioridade do board (menor = mais prioritário) |
| `boards.<id>.parallel` | boolean | `true` | Se `false`, máximo 1 tarefa ativa por vez |
| `boards.<id>.debt_target` | boolean | `false` | Board receptor de débitos automáticos |
| `boards.<id>.todo` | string | — | Coluna de entrada para novas issues/débitos |
| `boards.<id>.columns.<col>.subscribable_agent` | boolean | `false` | Permite override do agente padrão por issue |

---

## US-09: Desbloqueio automático ao concluir débito

**Épico**: Épico 4 — Mecanismo de Criação de Débitos

**Como** esteira agêntica,
**Quero** que ao concluir (fechar) uma issue de débito, a issue-pai seja automaticamente desbloqueada,
**Para que** a tarefa original volte a ser elegível sem intervenção manual.

### Comportamento esperado

1. Quando uma issue é movida para coluna terminal (concluído), verificar se o body contém `parent: #<N>`.
2. Se sim, remover label `blocked` da issue `#<N>`.
3. A issue `#<N>` volta a ser elegível na próxima varredura (US-02).

### Critérios de Aceitação

| # | Critério |
|---|----------|
| 1 | Ao concluir issue com `parent: #<N>` no body, remove label `blocked` de `#<N>`. |
| 2 | Se `#<N>` não existe ou já está desbloqueada, não falha (operação idempotente). |
| 3 | Log: `[HH:MM:SS] ℹ #<N> desbloqueada (débito #<M> concluído)`. |
| 4 | Na próxima varredura, `#<N>` é elegível novamente. |

---

## Dependências entre User Stories

```
US-01 (ciclo multi-board por prioridade)
 └── US-02 (seleção de tarefa) — executa dentro de US-01
      ├── US-03 (paralelismo) — restrição antes de US-02
      ├── US-04 (contador/delay) — consome resultado de US-02
      └── US-07 (gates) — executa antes de US-02 em cada board
US-05 (débito humano) — pós-execução de tarefa (US-02)
 └── US-06 (débito agente) — variação de US-05
      └── US-09 (desbloqueio) — depende de US-05/US-06
US-08 (parametrização) — transversal a todas
```

## Ordem de implementação sugerida

1. **US-01** → Base do novo loop multi-board
2. **US-02** → Seleção de tarefa dentro do loop
3. **US-03** → Restrição de paralelismo (antes de US-02 ser invocada)
4. **US-07** → Processamento de gates (dentro do loop)
5. **US-04** → Contador e delay inteligente (governa o ciclo)
6. **US-05** → Débitos por dependência humana
7. **US-06** → Débitos por dependência de agente
8. **US-09** → Desbloqueio automático
9. **US-08** → Validação final de parametrização completa

---

## Glossário

| Termo | Definição |
|-------|-----------|
| Ciclo | Uma iteração completa sobre todos os boards configurados |
| Tarefa elegível | Issue não bloqueada, não em gate de aprovação, não em wait_children, em coluna com agente |
| Tarefa ativa | Issue em execução por agente, aguardando aprovação, ou aguardando filhos — naquele board |
| debt_target | Flag que identifica o board receptor de débitos automáticos |
| subscribable_agent | Flag que permite override do agente padrão numa coluna |
| Marcador de débito | Bloco HTML comment no output do agente que sinaliza dependência |
| Gate | Coluna com `git_merge: true` sem `agent` — requer aprovação humana |
