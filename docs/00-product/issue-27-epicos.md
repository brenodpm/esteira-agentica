# Issue #27 — Épicos

## Épico 1: Refatoração do State para Multi-Issue

**Objetivo**: Substituir o state unitário por uma estrutura que suporte múltiplas issues ativas simultaneamente.

**Escopo**:
- Redesenhar `state.json` para manter uma lista de issues em andamento, cada uma com seu board, coluna, step e status.
- Garantir que `run_once()` possa selecionar qual issue processar sem depender de um único slot.
- Manter backward-compatibility na migração (state antigo → novo formato).

---

## Épico 2: Loop Multi-Board com Prioridade e Contador

**Objetivo**: Implementar o ciclo correto de varredura por boards.

**Escopo**:
- Ordenar boards por `priority` (menor = mais prioritário).
- Dentro de cada board, buscar próxima tarefa elegível (não bloqueada, mais antiga por `createdAt`).
- Se a tarefa estiver bloqueada ou em gate humano, pular para a próxima.
- Se nenhuma tarefa disponível no board, passar ao próximo.
- Implementar contador de execuções no ciclo:
  - A cada execução de agente iniciada: `contador += 1`.
  - Ao final do ciclo: se `contador > 0` → novo ciclo imediato; se `contador == 0` → delay com `pipe.agent.timeout.sleeptime`.

---

## Épico 3: Controle de Paralelismo por Board

**Objetivo**: Respeitar a regra `parallel: false` limitando execuções simultâneas por board.

**Escopo**:
- Quando `boards.<id>.parallel` = `false`, apenas uma issue pode estar ativa (em execução ou aguardando aprovação) naquele board por vez.
- "Ativa" significa: issue com status diferente de `idle` e diferente de `blocked` para aquele board.
- Quando `parallel: true` (ou não definido), não há limite — múltiplas issues do board podem avançar independentemente.
- Criar parâmetro `boards.<id>.max_parallel` (opcional) para controle numérico fino no futuro (default: 1 quando `parallel: false`, ilimitado quando `true`).

---

## Épico 4: Mecanismo de Criação de Débitos

**Objetivo**: Permitir que a esteira crie automaticamente issues de débito quando uma tarefa depende de input externo.

**Escopo**:
- Criar parâmetro `boards.<id>.debt_target: true` para indicar qual board recebe débitos técnicos criados automaticamente.
- Ao detectar dependência de resposta humana ou de outro agente:
  1. Criar issue no board marcado com `debt_target: true`.
  2. Marcar a issue original como `blocked` referenciando a nova issue.
  3. Permitir override do agente responsável pela resolução do débito via campo na issue (ex: `assigned_agent: <nome>`), sobrescrevendo o agente default da coluna do board de débitos.
- Criar parâmetro `boards.<id>.columns.<col>.subscribable_agent: true` para indicar que aquela coluna permite override de agente por issue.

---

## Épico 5: Parametrização do Delay e Configuração Declarativa

**Objetivo**: Garantir que toda regra de comportamento seja derivada de parâmetros explícitos no `esteira.yml`.

**Escopo**:
- O delay entre ciclos usa `pipe.agent.timeout.sleeptime` (já existe, em minutos).
- Garantir que o delay **só se aplique quando nenhuma tarefa foi executada** no ciclo (comportamento do contador).
- Documentar todos os novos parâmetros:
  - `boards.<id>.parallel` — controle de paralelismo (boolean).
  - `boards.<id>.max_parallel` — limite numérico opcional (int).
  - `boards.<id>.debt_target` — indica board-alvo para débitos (boolean).
  - `boards.<id>.columns.<col>.subscribable_agent` — permite override de agente (boolean).
- Nenhuma string ou board-name hardcoded no código — toda referência por atributo/flag.

---

## Dependências entre Épicos

```
Épico 1 (state multi-issue)
    └── Épico 2 (loop multi-board) depende de Épico 1
        └── Épico 3 (paralelismo) depende de Épico 2
Épico 4 (débitos) — independente, pode ser paralelizado com Épicos 2-3
Épico 5 (parametrização) — transversal, evolui junto com cada épico
```

## Critérios de Sucesso

- A esteira nunca fica ociosa em `aguardando aprovação` se existem tarefas disponíveis em outros boards.
- O log mostra execução contínua de múltiplas tasks entre aprovações.
- O campo `parallel: false` impede processamento concorrente no mesmo board.
- Débitos criados automaticamente aparecem no board correto com agente atribuído.
- Todos os comportamentos derivam de parâmetros explícitos no YAML.
