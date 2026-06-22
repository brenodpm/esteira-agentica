# Contexto e Decisões — Esteira Agêntica

Data: 2026-06-09

## Visão Geral

Sincronizador bidirecional entre GitHub Projects V2 e sistema de arquivos local.
Reescrita completa do projeto `esteira-agentica-ruim` com lógica nova.

- A anotação `/bloked_by` serve para indicar que a issue que possui esta anotação em seu body está aguardando a conclusão da tarefa que ela está referenciando ex: task 3 está aguardando o bug 5 concluir, no body da task 3 contém '/blocked_by 5', enquanto no bug 5 não tem nada, desta forma quando a esteira for buscar a proxima tarefa a ser executada ela pula a task 3 e executa o bug 5.]

## Regra de Prioridade (imutável)

1. **pipe.yml** — fonte da verdade para estrutura de boards/colunas
2. **Disco local** — reflete o pipe.yml; movimentação de issues propaga para o GitHub
3. **GitHub** — recebe atualizações; nunca sobrescreve pipe.yml ou estrutura local

## Propriedades Globais de Boards

| Campo          | Descrição                                                            |
|----------------|----------------------------------------------------------------------|
| `boards.bugs`  | ID do board onde bugs são criados.                                    |
| `boards.needs` | ID do board onde demandas para humanos ou outros agentes são criadas. |

## Propriedades de Colunas

| Campo       | Descrição                                                                                     |
|-------------|-----------------------------------------------------------------------------------------------|
| `effort`    | Nível de raciocínio do agente: `low`, `medium` ou `high`. Opcional, padrão `medium`. Níveis mais altos gastam mais tokens em análise profunda; níveis mais baixos produzem respostas mais rápidas. |
| `gitevents` | Lista opcional de eventos git da coluna: `create` (cria branch conforme gitflow), `keep` (padrão — branch já existe e é mantida), `merge` (solicita merge request ao concluir). Aceita combinação de eventos. |
| `allow-overwrite` | Se `true`, permite que a tag `/effort` na issue sobrescreva model e effort da coluna. Padrão: `false`. |

## Estrutura de Diretórios

```
.pipe/
  snapshot.json            # estado do último sync
  boards/
    <board-id>/
      <col-id>/
        <id>-<slug>.md           # arquivo principal da issue
        <id>-<slug>-history.md   # comentários (somente leitura)
        <id>-<slug>-write.md     # preencher = postar comentário
```

## Snapshot (`.pipe/snapshot.json`)

```json
{
  "pipe_mtime": "<mtime do pipe.yml>",
  "last_sync": "2026-06-08T22:50:00Z",
  "boards": {
    "<board-id>": ["<col-id>", ...]
  },
  "issues": {
    "<board-id>": [
      {
        "id": 27,
        "name": "Título sem . e sem -",
        "column": "<col-id>",
        "path": ".pipe/boards/board/col/27-slug.md",
        "history_path": ".pipe/boards/board/col/27-slug-history.md",
        "write_path": ".pipe/boards/board/col/27-slug-write.md",
        "l-time": "<mtime do arquivo local>",
        "b-time": "<updatedAt da issue no GitHub>",
        "status": "ok"
      }
    ]
  }
}
```

## Status de Issues

| Status | Significado |
|--------|-------------|
| `b-new` | Criado no board, precisa ser criado localmente |
| `l-new` | Criado localmente, precisa ser criado no board |
| `ok` | Sincronizado (existe local e no board) |
| `l-del` | Removido localmente, precisa ser removido no board |
| `b-del` | Removido no board, precisa ser removido localmente |
| `l-sync` | Arquivo local modificado (body, coluna ou write), precisa atualizar o board |
| `b-sync` | Board modificado (body, coluna ou comentários), precisa atualizar localmente |

## Regras de Detecção (QUANDO/ENTÃO)

### Full Sync
QUANDO `last_sync` for do dia anterior → full sync, `last_sync` = 00:00 UTC do dia atual

### Detecção de remoção
- QUANDO issue no snapshot mas não no board → `status=b-del`, `b-time=agora`
- QUANDO issue no snapshot mas não no diretório → `status=l-del`, `l-time=agora`

### Detecção de movimentação
- QUANDO issue no snapshot mas em coluna local diferente → `status=l-sync`, atualiza paths
- QUANDO issue no snapshot com `status=ok` e coluna no board diferente → `status=b-sync`

### Detecção de modificação
- QUANDO mtime do slug ou write > `l-time` → `status=l-sync`, `l-time=mtime`
- QUANDO `updatedAt` do board ≠ `b-time` → `status=b-sync`, `b-time=updatedAt`

### Detecção de criação
- QUANDO arquivo no diretório sem entrada no snapshot → `status=l-new`
- QUANDO issue no board sem entrada no snapshot → `status=b-new`

## Ações por Status

### Implementadas (board → local)

| Status | Ação |
|--------|------|
| `b-new` | Cria 3 arquivos (slug, history, write), preenche campos, status→ok |
| `b-del` | Remove 3 arquivos locais, remove do snapshot |
| `b-sync` | Atualiza body/history, move arquivos se coluna mudou, status→ok |

### Pendências (local → GitHub) — TODO

| Status | Ação |
|--------|------|
| `l-new` | Criar issue no GitHub, apagar arquivo original, recriar com padrão correto, status→ok |
| `l-del` | Fechar issue no GitHub, remover do board, remover do snapshot |
| `l-sync` | Mover card se coluna mudou, atualizar body se mudou, checar write (postar comentário se conteúdo), status→ok |

## Regra de Órfãos (ao mover slug)

QUANDO slug for movido de diretório:
- Se history ficou no diretório anterior → remover
- Se write ficou no diretório anterior com conteúdo → postar como comentário e remover
- O sync cria novos no diretório correto

## Arquivos por Issue

### Principal (`<id>-<slug>.md`)
- Contém: `# Título\n\n<body>`
- Leitura e escrita

### History (`<id>-<slug>-history.md`)
- **Somente leitura** — gerado do GitHub
- Formato: `<author> - <data>\n<body>\n--------`

### Write (`<id>-<slug>-write.md`)
- Criado **vazio**
- Se preenchido → conteúdo vira comentário na issue → arquivo limpo após envio

## Naming

- Arquivo: `<id>-<title em snake_case sem acentos/especiais>.md`
- Campo `name`: título sem `.` e sem `-`
- `_slugify`: normaliza Unicode, remove acentos, lowercase, não-alfanuméricos→`_`

## Otimização de API

### Consumo por ciclo de sync (5 boards, 20 issues)

**Antes (código original):**

| Operação | Chamadas/ciclo |
|----------|----------------|
| `_resolve_owner` | 5 (1 por board) |
| `_list_projects` | 5 |
| `gh project item-list` (REST) | 5 |
| `gh issue list --search updated` | 1 |
| `gh issue list --json createdAt` | 1 |
| Por movimentação (`move_card`) | 3-4 cada |
| **Total estimado** | ~17 + 4×moves |

**Depois (com cache):**

| Operação | Chamadas/ciclo |
|----------|----------------|
| `resolve_project_metadata` | 0 (cache hit) |
| `fetch_board_items_graphql` (1 query/board, apenas na virada de dia) | 0 no loop normal |
| `gh issue list --search updated` | 1 |
| Por movimentação (`move_card`) | 1 (só mutation, item_id do cache) |
| **Total estimado** | ~1 + 1×moves |

**Redução**: ~75-90% menos chamadas API por ciclo normal. Full sync (virada de dia): 5 queries GraphQL + 1 REST. Mutations com 1s de intervalo entre si.

### Estratégia de cache

- `project_id`, `status_field_id`, `options` e `items` cacheados no snapshot
- Cache populado na inicialização e atualizado incrementalmente
- Virada de dia refresh completo do cache via `full_sync()`
- Rate limit: `_mutation_throttle()` garante 1s entre mutations consecutivas

## Tratamento de Erros

- `RateLimitError` — detecta "rate limit" na resposta, pula o ciclo
- `GitHubError` — erro genérico, loga e continua
- Loop principal com catch-all para não morrer
- `_build_history` falha graciosamente (retorna vazio)

## Tecnologias

- Python 3.14
- PyYAML para config
- `gh` CLI para GitHub (GraphQL + REST)
- Sem banco de dados — snapshot.json é o estado
- Execução: `python -m src`
