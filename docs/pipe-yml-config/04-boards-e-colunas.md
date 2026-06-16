# Configuração de Boards e Colunas

Boards são o núcleo organizacional da esteira. Cada board sincroniza com um GitHub Project V2 e contém um workflow definido por colunas.

## Estrutura Base

```yaml
boards:
  bugs: bug                    # ID do board para bugs (usado internamente)
  needs: debito                # ID do board para demandas de humanos/agentes
  create-remote-boards: true   # Cria boards remotos automaticamente se não existirem
  allow-del-remote-issue: true # Permite deletar issues remotas

  <board-id>:                  # Define um novo board
    name: "..."                # Nome no GitHub Projects
    todo: backlog              # ID da coluna inicial
    priority: 0                # Ordem de processamento (0 = mais alta)
    flow: epic                 # Gitflow associado
    parallel: false            # Processa uma issue por vez ou em paralelo
    columns:
      <col-id>:               # Define uma coluna dentro do board
        # ... configuração da coluna
```

## Configurações de Board

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `name` | Nome visível no GitHub Projects | `"User Stories"` |
| `todo` | ID da coluna onde issues novas entram | `backlog` |
| `priority` | Ordem de processamento (0 = maior) | `0`, `1`, `2` |
| `flow` | Gitflow usado por issues deste board | `feature`, `epic`, `bugfix` |
| `parallel` | Se `false`, processa uma issue por vez | `true`/`false` |

## Configurações de Coluna

```yaml
columns:
  backlog:                     # ID único da coluna
    name: Backlog              # Nome visível no GitHub Projects
    desc: "..."                # Descrição do que acontece aqui
    agent: requirements        # Agente responsável (se ausente = manual)
    effort: high               # Nível de esforço (low, medium, high)
    gitevents: [create, merge] # Eventos git executados aqui
    acao: "..."                # Instrução para o agente
    git_commit: true           # Faz commit das alterações
    git_merge: true            # Envolve criação de PR/merge
    wait_children: false       # Aguarda issues filhas terminarem
    allow-overwrite: true      # Permite `/effort` na issue sobrescrever
    change:                    # Transições para outras colunas
      advance: proxima_coluna
      reprovar: backlog
      falha: desenvolvimento
      bloquear: blocked
      cancelar: cancelado
```

### Eventos Git (gitevents)

- **create**: Cria branch conforme gitflow da issue quando chega nessa coluna
- **keep**: Mantém branch existente (padrão se não especificado)
- **merge**: Solicita merge request / PR quando sai da coluna

### Transições (change)

Define para onde a issue se move após cada resultado:

- **advance**: Transição normal após conclusão
- **reprovar**: Retorna para revisão humana
- **cancelar**: Move para coluna cancelada
- **falha**: Retorna ao desenvolvimento se testes falharem
- **bloquear**: Coluna de bloqueio por dependência externa

## Exemplo Prático: Board "User Stories"

```yaml
story:
  name: "User Stories"
  todo: backlog
  priority: 3
  flow: epic
  columns:
    backlog:
      name: Backlog
      desc: "Story aguardando início"
      change:
        advance: requisitos
        cancelar: cancelado

    requisitos:
      name: "Requisitos"
      desc: "Agente levanta requisitos funcionais e não-funcionais"
      agent: requirements
      gitevents: [create]
      acao: "Entender demanda, entrevistar usuário, criar documentações"
      change:
        advance: validacao-negocial

    validacao-negocial:
      name: "Validação"
      desc: "Humano valida documentação"
      change:
        advance: arquitetura
        reprovar: requisitos

    arquitetura:
      name: "Arquitetura"
      agent: architecture
      effort: high
      acao: "Definir arquitetura técnica"
      change:
        advance: desenvolvimento

    desenvolvimento:
      name: "Desenvolvimento"
      agent: engineering
      effort: high
      gitevents: [merge]
      acao: "Implementar conforme arquitetura aprovada"
      change:
        advance: concluido

    concluido:
      name: "Concluído"
```

## Boas Práticas

1. **Ordene colunas conforme o fluxo natural** de trabalho
2. **Cada coluna com `agent`** deve ter uma `acao` clara
3. **Use `priority`** para controlar qual board é processado primeiro
4. **Colunas manuais** (sem agente) são revisão humana
5. **`wait_children`** é útil quando há dependências (ex: épicos aguardam stories)
6. **Mantenha nomes de coluna curtos** (compatível com GitHub Projects)
