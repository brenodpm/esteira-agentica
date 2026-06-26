# Contexto e Decisões — Esteira Agêntica v2

Data: 2026-06-26

## Visão Geral

Esteira automatizada de agentes de IA com arquitetura hexagonal. Reescrita do projeto `oldversion/` para suportar múltiplas plataformas de board (GitHub Projects, ClickUp, etc).

## Arquitetura Hexagonal

```
src/
├── core/               # Domínio - regras de negócio
│   ├── log.py          # Logging dual (terminal resumo + arquivo detalhe)
│   ├── config.py       # Validação do pipe.yml
│   ├── board.py        # Board core + BoardPort (interface)
│   └── snapshot.py     # Snapshot por board (.pipe/boards/<id>/snapshot.json)
├── adapters/           # Implementações de ports
│   └── github_board.py # Adapter para GitHub Projects V2
└── __main__.py         # Orquestração
```

### Ports e Adapters

- **BoardPort** — interface abstrata para operações de board
- **Board** — core que usa o port para operações
- Adapters implementam BoardPort para cada plataforma

## Fluxo Principal

```
main()
├── check_config()      # Valida pipe.yml e variáveis de ambiente
├── startup()           # Configura SSH e clona repositórios
├── first_board_sync()  # Cria diretórios, sync local e remoto
│   ├── Cria .pipe/boards/<board_id>/<col_id>/
│   ├── Sincroniza snapshot local (mapa de colunas)
│   ├── sync_boards() remoto (com retry de penalty)
│   └── detect_board_changes() por board
│
└── while running:      # Loop principal (TODO)
    ├── sync_board()
    ├── keep_task()
    ├── call_agent()
    └── sleep_time()
```

## Configuração (pipe.yml)

```yaml
log:
  dir: logs                    # Caminho dos arquivos de log
  ttl: 10                      # Dias de retenção dos logs
  level: INFO                  # Nível de log

git:
  repo:
    <id-repo>: <url>          # Repositórios a clonar (SSH)
  flow:
    base: main                 # Branch principal
    <id-flow>:
      name | prefix: ...       # Branch fixa ou prefixo
      create: <id>             # Origem para criar branch
      merge: <id>              # Destino do merge request

agents:
  <id-platform>:               # Ex: kiro-cli
    <id-agent>:
      name: <nome>
      <properties>: ...

boards:
  platform: github             # Plataforma do board (github, clickup)
  <id-board>:
    name: <nome>
    todo: <coluna-inicial>     # Opcional
    priority: <n>              # 0 = maior prioridade
    flow: <id-flow>            # Opcional
    parallel: true|false       # Opcional, default true
    columns:
      <id-column>:
        name: <nome>
        agent: <id-agent>      # Opcional, se vazio é tarefa humana
        effort: low|medium|high
        prompt: <comando>
        archive: true|false
        gitevents: [create|merge]
        change:
          advance: <id-column>
          <id>: <id-column>
```

## Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| `PIPE_SSH_KEY_FILE` | Caminho para chave SSH (ex: `~/.ssh/id_ed25519_esteira`) |

## Decisões Técnicas

### Log (core)
- Singleton com dual output: terminal (resumo colorido) + arquivo (detalhe)
- Terminal: `[Módulo] mensagem` com cores por nível
- Arquivo: `timestamp - LEVEL - module - mensagem | {extras}`
- Extras são kwargs opcionais que vão só para o arquivo (ex: project_id, query, error)
- Exceções via `exc=` incluem traceback completo no arquivo
- Arquivo diário: `logs/yyyy-MM-dd.json`
- Cleanup automático: remove logs com mais de `ttl` dias
- `separator()`: linha em branco no arquivo para demarcar início de execução
- Parâmetros configuráveis via pipe.yml: `log.dir`, `log.ttl`, `log.level`

### Snapshot (core)
- Um snapshot por board: `.pipe/boards/<board_id>/snapshot.json`
- Estrutura: `{board: {col_id: col_name}, issues: [...], last_sync: "iso"}`
- `Snapshot(board_id)` — instanciado por board

### SSH
- Chave copiada para `~/.ssh/id_pipe` (não sobrescreve chaves existentes)
- Configurado em `~/.ssh/config` para usar apenas no github.com
- Variável aponta para arquivo (não conteúdo) para evitar problemas com caracteres especiais

### Repositórios
- Clonados em `repo/<id-repo>/`
- Startup sincroniza: clona faltantes, remove extras

### Board
- Core (`Board`) não conhece implementação específica
- Port (`BoardPort`) define interface para adapters
- `sync_boards()` recebe lista ordenada por prioridade: `[{id, name, columns}, ...]`
- `PenaltyException(wait_seconds)` para sinalizar rate limit (mínimo 1s)

## GitHub Adapter

### Throttle (controle de velocidade)
- `_throttle_value`: segundos de sleep antes de cada chamada (inicia em 16)
- `_throttle_cooldown`: timestamp para regredir o valor (1h sem problemas → divide por 2)
- `_throttle()`: executa sleep e gerencia regressão
- `_throttle_hit()`: dobra valor (até 64s), se já for 64 → ativa penalty

### Penalty (bloqueio temporário)
- `_in_penalty`: flag se está bloqueado
- `_penalty_value`: horas de bloqueio (inicia em 1, dobra a cada hit)
- `_penalty_ttl`: timestamp de quando o penalty expira
- `_penalty_cooldown`: timestamp para regredir o valor
- `_penalty_check()`: verifica estado, desativa se expirou, regride após cooldown
- `_penalty_hit()`: ativa penalty por N horas, retorna PenaltyException

### Rate Limit Handling
- **Primary rate limit**: consulta `GET /rate_limit` para saber tempo de reset
- **Secondary rate limit**: extrai `retry-after` do header, chama `_throttle_hit()`
- Retry automático após sleep em ambos os casos

### Offline Handling
- Detecta falta de conexão via padrões no stderr (ex: "could not resolve host", "timeout")
- Backoff crescente: 1s, 2s, 4s... até 300s
- **Importante**: só verifica offline quando `returncode != 0` (evita falso positivo com conteúdo de issues)

### list_issues — Paginação
- Page size: 5 items por request (minimiza risco de secondary rate limit)
- Paginação via cursor GraphQL (`pageInfo.hasNextPage`, `endCursor`)
- Log de progresso a partir da página 2

### Métodos de API
| Método | Função |
|--------|--------|
| `_gh()` | Executa comando gh CLI com retry |
| `_gql()` | Executa GraphQL via gh com retry |
| `_resolve_owner()` | Descobre se owner é user/org |
| `_list_projects()` | Lista projects V2 do owner |
| `_create_project()` | Cria novo project |
| `_get_status_field()` | Busca campo Status |
| `_create_status_field()` | Cria campo Status com colunas |
| `_update_status_options()` | Atualiza opções do Status |

### Métodos Implementados
- `connect()` — extrai repositório do config
- `sync_boards()` — sincroniza boards/colunas com GitHub Projects
- `list_issues()` — lista issues de um board (paginado)

### Métodos Pendentes
- `get_issue()` — buscar issue específica
- `move_issue()` — mover issue para outra coluna
- `update_issue()` — atualizar body da issue
- `add_comment()` — adicionar comentário

## Validações (check_config)

- `PIPE_SSH_KEY_FILE` existe e arquivo existe
- `git.repo` obrigatório
- `git.flow.base` obrigatório
- `git.flow.<id>` requer `name` ou `prefix`
- `agents.<platform>.<agent>.name` obrigatório
- `boards.platform` obrigatório
- `boards.<id>.name` obrigatório
- `boards.<id>.columns.<col>.name` obrigatório
- `log.ttl` se presente, deve ser inteiro >= 1

## Bugs Corrigidos

- **Falso positivo de offline**: `_gql` verificava offline mesmo com `returncode == 0`, matchando palavras como "timeout" no body das issues
- **Busy loop de penalty**: `int()` truncava `wait_seconds` para 0, causando loop infinito. Fix: `max(1, int(...))`

## Pendências Gerais

- [ ] Implementar métodos restantes do GitHub adapter
- [ ] Implementar adapter ClickUp
- [ ] Implementar sync_board() no loop (detecção de movimentos)
- [ ] Implementar keep_task()
- [ ] Implementar call_agent()
- [ ] Implementar sleep_time()
