# Issue #27 — User Stories

Status: draft
Owner: product-agent
Last updated: 2026-06-08T12:56:00-03:00

---

## US-01: State Multi-Issue

**Como** esteira agêntica,
**Quero** manter múltiplas issues ativas simultaneamente no state,
**Para que** uma issue em gate de aprovação não impeça o processamento de outras.

### Critérios de Aceitação

1. O `state.json` passa a armazenar uma lista de issues ativas (`issues: [...]`), cada uma com: `issue_number`, `current_feature`, `current_board`, `current_column`, `current_step`, `status`, `rework`.
2. A migração do formato antigo (state unitário) para o novo formato ocorre automaticamente ao carregar um state no formato legado.
3. `run_once()` itera sobre as issues ativas e seleciona qual processar com base na prioridade do board.
4. Issues com `status: awaiting_approval` são ignoradas na seleção — a esteira busca outra issue elegível.
5. Issues com `status: blocked` são ignoradas na seleção.
6. O parâmetro `pipe.state.path` no `esteira.yml` define o caminho do arquivo de state (default: `state.json`).

### Notas Técnicas

- O módulo `src/orchestrator/state.py` deve ser refatorado para suportar o novo schema.
- A função `_reset_state` opera sobre um item da lista, não sobre o state inteiro.

---

## US-02: Loop Multi-Board com Varredura por Prioridade

**Como** esteira agêntica,
**Quero** varrer todos os boards em cada ciclo, ordenados por prioridade (menor valor = maior prioridade),
**Para que** tarefas de alta prioridade nunca fiquem paradas por causa de tarefas de baixa prioridade em gate.

### Critérios de Aceitação

1. A cada ciclo, os boards são ordenados pelo campo `boards.<id>.priority` (menor valor primeiro).
2. Dentro de cada board, busca-se a próxima tarefa elegível: não bloqueada, não em coluna terminal, não em gate humano, ordenada por `createdAt` (mais antiga primeiro).
3. Se a tarefa retornada estiver bloqueada, busca a próxima tarefa do mesmo board.
4. Se não houver tarefas elegíveis no board atual, passa-se para o próximo board na lista.
5. A busca percorre todos os boards até encontrar uma tarefa ou encerrar sem nenhuma.
6. A propriedade `boards.<id>.priority` é obrigatória para todos os boards definidos.

### Notas Técnicas

- A lógica atual de `priority.select_next` já agrupa por priority; o ajuste principal é a interação com o state multi-issue e o respeito a paralelismo.

---

## US-03: Contador de Execuções e Delay Condicional

**Como** esteira agêntica,
**Quero** que o delay entre ciclos só se aplique quando nenhuma tarefa foi executada no ciclo,
**Para que** a esteira não fique ociosa artificialmente quando há trabalho disponível.

### Critérios de Aceitação

1. No início de cada ciclo, um contador de execuções é inicializado em `0`.
2. A cada execução de agente iniciada com sucesso no ciclo, o contador é incrementado em `1`.
3. Ao final do ciclo (após varrer todos os boards):
   - Se `contador > 0`: inicia novo ciclo imediatamente (sem delay).
   - Se `contador == 0`: aplica delay usando o valor de `pipe.agent.timeout.sleeptime` (em minutos, conforme já existe no yml).
4. O parâmetro `pipe.agent.timeout.sleeptime` define o tempo de espera em minutos quando não há trabalho.
5. O log exibe o contador ao final de cada ciclo para rastreabilidade.

### Notas Técnicas

- O `run_loop` atual aplica `time.sleep` incondicionalmente — deve ser condicional ao contador.

---

## US-04: Controle de Paralelismo por Board

**Como** esteira agêntica,
**Quero** respeitar o parâmetro `parallel` de cada board para limitar a execução simultânea,
**Para que** boards com `parallel: false` tenham no máximo uma tarefa ativa por vez.

### Critérios de Aceitação

1. Quando `boards.<id>.parallel` é `false`, apenas **uma** issue daquele board pode estar com status diferente de `idle` e diferente de `blocked` no state (ativa = executando ou em gate).
2. Quando `boards.<id>.parallel` é `true` (ou omitido), não há limite de issues ativas para aquele board.
3. Ao buscar tarefa em um board com `parallel: false`, se já houver uma issue ativa para aquele board no state, o board é pulado.
4. O parâmetro opcional `boards.<id>.max_parallel` (int) permite controle numérico fino no futuro. Default: `1` quando `parallel: false`, ilimitado quando `parallel: true`.
5. "Issue ativa" para este controle significa: issue no state com `status` em `{awaiting_approval, executing}` para o board em questão.

### Notas Técnicas

- A verificação de paralelismo ocorre antes da seleção de tarefa dentro do board.

---

## US-05: Criação Automática de Débitos por Dependência Humana

**Como** esteira agêntica,
**Quero** criar automaticamente uma issue de débito quando uma tarefa depende de resposta humana,
**Para que** a tarefa original seja desbloqueada após a intervenção e o débito fique rastreável.

### Critérios de Aceitação

1. O parâmetro `boards.<id>.debt_target: true` indica qual board é o destino de débitos criados automaticamente. Exatamente um board deve ter este parâmetro.
2. Quando um agente detecta necessidade de resposta humana, a esteira:
   - Cria uma issue no board marcado com `debt_target: true`.
   - Adiciona label `needs-human` à issue de débito.
   - Marca a issue original como `blocked` referenciando a issue de débito no body.
3. A issue de débito inclui no body: contexto da dependência, referência à issue bloqueada (`Parent: #N`), e label do board de destino.
4. Quando a issue de débito é resolvida (fechada), o mecanismo `unblock_dependents` remove o bloqueio da issue original.
5. A detecção de "necessidade de resposta humana" é sinalizada pelo agente via output estruturado (ex: marcador `[NEEDS_HUMAN]` no output).
6. O parâmetro `pipe.debt.human_marker` define o marcador que o agente usa para sinalizar dependência humana (default: `[NEEDS_HUMAN]`).

### Notas Técnicas

- Reutiliza `blocker.create_blocker` existente, apenas parametrizando o board-alvo.

---

## US-06: Criação Automática de Débitos por Dependência de Agente

**Como** esteira agêntica,
**Quero** criar automaticamente uma issue de débito quando uma tarefa depende de outro agente,
**Para que** o agente responsável seja subscrito e resolva o débito sem intervenção humana.

### Critérios de Aceitação

1. Quando um agente detecta necessidade de resposta de outro agente, a esteira:
   - Cria uma issue no board marcado com `debt_target: true`.
   - Marca a issue original como `blocked` referenciando a issue de débito.
2. O parâmetro `boards.<id>.columns.<col>.subscribable_agent: true` indica que aquela coluna permite override do agente executor por issue.
3. A issue de débito pode especificar um agente específico via campo no body: `Assigned-Agent: <nome>`. Este agente sobrescreve o `agent` definido na coluna do board de débitos.
4. Quando não há `Assigned-Agent` no body da issue, usa-se o agente padrão definido na coluna.
5. A detecção de "necessidade de outro agente" é sinalizada pelo agente via output estruturado (ex: marcador `[NEEDS_AGENT:<nome>]`).
6. O parâmetro `pipe.debt.agent_marker` define o padrão do marcador (default: `[NEEDS_AGENT:{agent}]`).

### Notas Técnicas

- O runner deve parsear o output do agente após execução para detectar os marcadores.
- O campo `Assigned-Agent` no body é lido pelo runner ao iniciar a execução da issue de débito.

---

## US-07: Parametrização Completa sem Valores Hardcoded

**Como** desenvolvedor da esteira,
**Quero** que toda regra de comportamento derive de parâmetros explícitos no `esteira.yml`,
**Para que** a configuração seja declarativa, extensível e sem magic strings no código.

### Critérios de Aceitação

1. Novos parâmetros a serem definidos no `esteira.yml`:
   - `pipe.state.path` — caminho do arquivo de state (default: `state.json`).
   - `pipe.debt.human_marker` — marcador de dependência humana no output do agente (default: `[NEEDS_HUMAN]`).
   - `pipe.debt.agent_marker` — padrão do marcador de dependência de agente (default: `[NEEDS_AGENT:{agent}]`).
   - `boards.<id>.parallel` — boolean, controle de paralelismo (já existe).
   - `boards.<id>.max_parallel` — int opcional, limite numérico de issues ativas.
   - `boards.<id>.debt_target` — boolean, indica board-alvo para débitos automáticos.
   - `boards.<id>.columns.<col>.subscribable_agent` — boolean, permite override de agente por issue.
2. Nenhuma referência hardcoded a nomes de boards (ex: `"debito"`, `"bug"`) no código-fonte.
3. O código deve buscar o board de débitos via atributo `debt_target: true`, não por nome.
4. O código deve buscar a coluna com override de agente via `subscribable_agent: true`, não por nome.
5. Todos os parâmetros possuem defaults documentados e a esteira funciona sem que todos sejam explicitados.

### Notas Técnicas

- O módulo `src/config/loader.py` deve ser atualizado para reconhecer os novos parâmetros e aplicar defaults.

---

## US-08: Avanço Automático por Colunas sem Agente

**Como** esteira agêntica,
**Quero** que colunas sem agente e sem `wait_children` que não sejam terminais funcionem como gates humanos,
**Para que** a movimentação entre colunas siga o fluxo sem ficar presa.

### Critérios de Aceitação

1. Coluna sem `agent`, sem `wait_children`, com `change.advance` definido = gate humano → issue entra em `awaiting_approval`.
2. Coluna sem `agent`, sem `wait_children`, sem `change` (nenhum) = terminal → issue é finalizada.
3. Coluna `todo` é avançada automaticamente para a próxima coluna (já implementado).
4. A esteira não fica presa em colunas que não requerem ação — ou é gate humano (e a esteira segue para outra issue) ou é terminal.

### Notas Técnicas

- Essa lógica já existe parcialmente no runner; precisa ser validada no contexto multi-issue.

---

## Resumo de Novos Parâmetros no `esteira.yml`

| Parâmetro | Tipo | Default | Descrição |
|---|---|---|---|
| `pipe.state.path` | string | `state.json` | Caminho do arquivo de state |
| `pipe.debt.human_marker` | string | `[NEEDS_HUMAN]` | Marcador no output do agente para dependência humana |
| `pipe.debt.agent_marker` | string | `[NEEDS_AGENT:{agent}]` | Padrão do marcador para dependência de agente |
| `boards.<id>.parallel` | boolean | `true` | Se `false`, limita a 1 issue ativa no board |
| `boards.<id>.max_parallel` | int | (ilimitado ou 1) | Limite numérico de issues ativas |
| `boards.<id>.debt_target` | boolean | `false` | Indica board-alvo para débitos automáticos |
| `boards.<id>.columns.<col>.subscribable_agent` | boolean | `false` | Permite override de agente por issue |

---

## Mapa de Dependências entre User Stories

```
US-01 (State Multi-Issue)
  └── US-02 (Loop Multi-Board) depende de US-01
      └── US-03 (Contador/Delay) depende de US-02
      └── US-04 (Paralelismo) depende de US-01 + US-02
US-05 (Débito Humano) depende de US-07
US-06 (Débito Agente) depende de US-07
US-07 (Parametrização) — independente, deve ser implementada primeiro ou em paralelo com US-01
US-08 (Avanço Automático) depende de US-01
```

## Ordem Sugerida de Implementação

1. US-07 (Parametrização) + US-01 (State Multi-Issue) — em paralelo
2. US-02 (Loop Multi-Board)
3. US-03 (Contador/Delay) + US-04 (Paralelismo) — em paralelo
4. US-08 (Avanço Automático)
5. US-05 (Débito Humano) + US-06 (Débito Agente) — em paralelo
