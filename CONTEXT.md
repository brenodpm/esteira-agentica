# Contexto e Decisões — Esteira Agêntica

Data: 2026-06-08

## Visão Geral

Sincronizador bidirecional entre GitHub Projects V2 e sistema de arquivos local.
Reescrita completa do projeto `esteira-agentica-ruim` com lógica nova.

## Regra de Prioridade (imutável)

1. **pipe.yml** — fonte da verdade para estrutura de boards/colunas
2. **Disco local** — reflete o pipe.yml; movimentação de issues propaga para o GitHub
3. **GitHub** — recebe atualizações; nunca sobrescreve pipe.yml ou estrutura local

O GitHub **nunca** dita a estrutura de diretórios. Sempre o contrário.

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

## Arquivos por Issue

### Principal (`<id>-<slug>.md`)
- Contém: `# Título\n\n<body da issue>`
- Leitura e escrita

### History (`<id>-<slug>-history.md`)
- **Somente leitura** — gerado a partir dos comentários do GitHub
- Formato:
  ```
  <author> - <data>
  <body>
  --------
  ```
- Atualizado toda vez que o arquivo principal é atualizado

### Write (`<id>-<slug>-write.md`)
- Criado sempre **vazio**
- Se preenchido → conteúdo vira comentário na issue do GitHub → arquivo limpo após envio

## Naming de Arquivos

- Formato: `<id>-<title em snake_case sem acentos e sem caracteres especiais>.md`
- O campo `name` no snapshot remove `.` e `-` do título original
- A função `_slugify` normaliza Unicode, remove acentos, converte para lowercase, troca não-alfanuméricos por `_`

## Sync de Estrutura (na inicialização)

1. Carrega `pipe.yml`
2. Compara `pipe_mtime` do snapshot com mtime real do arquivo
3. Se diferente: recria diretórios locais conforme pipe.yml (remove obsoletos, cria novos)
4. Push colunas para GitHub Projects V2 (cria projetos/campos Status se necessário)
5. Salva snapshot

## Sync de Issues (no loop principal)

1. Busca items de todos os boards via `gh project item-list`
2. Compara com snapshot — issues novas recebem status `b-new`
3. Para cada `b-new`: cria os 3 arquivos, busca comentários via `gh issue view`, preenche `itime` com `updatedAt`
4. Salva snapshot

## Loop Principal

```python
sync(config)  # estrutura
while True:
    sync_issues(config)  # issues
    time.sleep(sleeptime)
```

## Integração GitHub

- Usa `gh` CLI (não requer token manual, usa auth do gh)
- GraphQL para operações de Projects V2 (criar projeto, campos, opções)
- REST/CLI para issues (view, comments)
- `_gql()` não usa `check=True` pois erros parciais são esperados (org vs user)

## Pendências: Ações Local → GitHub (TODO)

| Ação | Trigger | Efeito no GitHub |
|------|---------|------------------|
| Criar issue | Arquivo novo em coluna (status `l-new`) | Criar issue no repo + adicionar ao project board |
| Mover issue | Arquivo movido de coluna (status `l-mv`) | Mover card para nova coluna no project |
| Deletar issue | Arquivo removido (status `l-del`) | Fechar issue no GitHub |
| Postar comentário | Arquivo `*-write.md` com conteúdo | Postar body como comentário na issue e limpar o arquivo |

## Tecnologias

- Python 3.14
- PyYAML para config
- `gh` CLI para GitHub
- Sem banco de dados — snapshot.json é o estado
- Execução: `python -m src`
