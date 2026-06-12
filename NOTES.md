# Contexto e Decisões — Esteira Agêntica

Data: 2026-06-09

## Visão Geral

Sincronizador bidirecional entre GitHub Projects V2 e sistema de arquivos local.
Reescrita completa do projeto `esteira-agentica-ruim` com lógica nova.

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
| `l-mv` | Movido localmente, precisa ser movido no board |
| `b-mv` | Movido no board, precisa ser movido localmente |
| `l-sync` | Arquivo local modificado, precisa atualizar o board |
| `b-sync` | Board modificado, precisa atualizar localmente |

## Regras de Detecção (QUANDO/ENTÃO)

### Full Sync
QUANDO `last_sync` for do dia anterior → full sync, `last_sync` = 00:00 UTC do dia atual

### Detecção de remoção
- QUANDO issue no snapshot mas não no board → `status=b-del`, `b-time=agora`
- QUANDO issue no snapshot mas não no diretório → `status=l-del`, `l-time=agora`

### Detecção de movimentação
- QUANDO issue no snapshot mas em coluna local diferente → `status=l-mv`, atualiza paths
- QUANDO issue no snapshot com `status=ok` e coluna no board diferente → `status=b-mv`

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
| `b-sync` | Atualiza history com comentários, atualiza body se mudou, status→ok |
| `b-mv` | Move 3 arquivos para nova coluna, atualiza history, status→ok |

### Pendências (local → GitHub) — TODO

| Status | Ação |
|--------|------|
| `l-new` | Criar issue no GitHub, apagar arquivo original, recriar com padrão correto, status→ok |
| `l-del` | Fechar issue no GitHub, remover do board, remover do snapshot |
| `l-mv` | Mover card no board, atualizar column, checar write, status→ok |
| `l-sync` | Atualizar body se principal mudou, checar write (postar comentário se conteúdo), status→ok |

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

- `last_sync` salvo no snapshot — próximos ciclos usam `gh issue list --search "updated:>=date"`
- Apenas issues modificadas são processadas
- `fetch_board_items` ainda busca lista completa (necessário para detectar `b-del`)
- Rate limit: 5000 pontos/hora (GraphQL), 5000 req/hora (REST), janela de 1 hora

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
