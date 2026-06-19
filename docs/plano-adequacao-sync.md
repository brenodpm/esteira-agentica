# Plano de Adequação — Sincronização de Issues

Data: 2026-06-15

## Análise de Falhas no Documento Original

Antes do plano, seguem problemas identificados no `melhoria-movimentacao-issues.md`:

1. **Etapa 3 e 4 duplicam lógica de b-sync**: A etapa 3 (GitHub→Snapshot) define ações para issues modificadas, mas a etapa 4 (Remoção de resíduos) repete exatamente a mesma lógica para status `b-sync`. Se a etapa 3 já seta o status para `ok`, não haverá `b-sync` na etapa 4. **Solução**: A etapa 4 deve tratar apenas `b-del` (limpeza) e issues que chegaram como `b-new` na virada de dia (criação local). O bloco `b-sync` na etapa 4 é redundante e deve ser removido ou usado apenas como fallback para issues que falharam na etapa 3.

2. **Falta de tratamento para `l-new` na sincronização de issues**: O documento define as 4 etapas mas não menciona onde `l-new` é executado (criar issue no GitHub). Está implícito na etapa 2 (snapshot→GitHub) mas não documentado explicitamente.

3. **Falta de tratamento para `b-new` na sincronização de loop**: Na sync de loop, não há menção a `b-new` — apenas a sync por virada de dia detecta issues novas do board. Se uma issue for criada no GitHub entre dois dias, ela só será detectada na virada. **Solução**: Adicionar detecção de `b-new` na etapa 3 (GitHub→Snapshot) comparando items retornados com snapshot existente.

4. **Conflito de precedência na movimentação bidirecional**: Se o usuário move localmente (l-sync com coluna diferente) e simultaneamente alguém move no GitHub, o documento não define qual vence. Pela regra de prioridade (local > GitHub), a etapa 2 deveria vencer, mas a etapa 3 sobrescreve. **Solução**: Na etapa 3, só aplicar mudança de coluna do GitHub se o status da issue no snapshot for `ok` (não `l-sync`).

5. **API não suporta filtro server-side por updatedAt nos ProjectV2 items**: O documento diz "consulta por modificação após a data/hora da ultima consulta" na etapa 3, mas a GraphQL API do GitHub **não oferece filtro temporal** nos items do Project. É necessário buscar todos os items e filtrar client-side. Já é o que o código faz hoje — o `gh issue list --search "updated:>=date"` funciona para issues REST, mas não para project items.

6. **Custo de API no `move_card` atual**: Cada movimentação gasta 3-4 chamadas (resolve_owner + list_projects + item-list + updateField). Com cache de IDs no snapshot, cai para 1 chamada (só a mutation updateProjectV2ItemFieldValue).

---

## Restrições de Rate Limit (GitHub API)

| Recurso | Limite | Observação |
|---------|--------|------------|
| GraphQL primary | 5.000 pts/hora | Queries simples = 1pt, paginadas escalam |
| GraphQL secondary (mutations) | 2.000 pts/min | Cada mutation = 5 pts |
| GraphQL secondary (queries) | 2.000 pts/min | Cada query = 1 pt |
| REST API | 5.000 req/hora | `gh issue list/view/edit` usa REST |
| Content creation | 80/min, 500/hora | Criar issues, comentários |

**Estratégia de minimização**: Cache agressivo de project_id, field_id, option_ids e item_ids no snapshot. Uma única GraphQL query por board para buscar todos os items com seus campos (substitui N chamadas REST).

---

## Plano de Implementação

### Fase 0 — Preparação (config e snapshot)

- [ ] 0.1. Adicionar atributo `boards.create-remote-boards` ao schema do `pipe.yml` (booleano, opcional, default=false)
- [ ] 0.2. Adicionar atributo `boards.allow-del-remote-issue` ao schema do `pipe.yml` (booleano, opcional, default=false)
- [ ] 0.3. Atualizar `config.py` → `load_config()` para expor `boards_meta["create-remote-boards"]` e `boards_meta["allow-del-remote-issue"]`
- [ ] 0.4. Remover status `l-mv` e `b-mv` do código — substituir por `l-sync` e `b-sync` respectivamente
- [ ] 0.5. Adicionar ao snapshot um bloco `cache` com estrutura: `{ "<board_id>": { "project_id": "...", "project_number": N, "status_field_id": "...", "options": { "<col_name>": "<option_id>" }, "items": { "<issue_number>": "<item_id>" } } }`
- [ ] 0.6. Atualizar `NOTES.md` e `README.md` para refletir a remoção de `l-mv`/`b-mv`

### Fase 1 — Otimização da camada GitHub (`github.py`)

- [ ] 1.1. Criar função `resolve_project_metadata(config, board_id, snapshot_cache)` que retorna project_id, field_id e options usando cache do snapshot (0 chamadas se cache válido, 2 chamadas se não)
- [ ] 1.2. Criar função `fetch_board_items_graphql(project_id)` usando uma única query GraphQL que retorna: item_id, content(number, title, url), fieldValues(Status → name), updatedAt do content — substituir o `gh project item-list` CLI
- [ ] 1.3. Reescrever `move_card()` para aceitar item_id direto do cache (1 mutation apenas: updateProjectV2ItemFieldValue) — se item_id não existe no cache, fazer `addProjectV2ItemById` (idempotente) e cachear o resultado
- [ ] 1.4. Criar função `add_issue_to_project(config, board_id, issue_node_id)` usando `addProjectV2ItemById` — retorna item_id, atualiza cache
- [ ] 1.5. Criar função `get_issue_node_id(repo, issue_number)` usando GraphQL (uma query para pegar o node_id da issue necessário para addProjectV2ItemById)
- [ ] 1.6. Remover chamadas redundantes de `_resolve_owner` e `_list_projects` nas funções que já podem usar o cache
- [ ] 1.7. Adicionar sleep de 1s entre mutations consecutivas (recomendação oficial do GitHub para evitar secondary rate limit)

### Fase 2 — Sincronização Inicial (`sync.py`)

- [ ] 2.1. Reescrever `sync()` para o fluxo de "projeto não existe" (sem snapshot.json): criar snapshot com estrutura base, criar diretórios, popular `cache` resolvendo metadata de cada board (se `create-remote-boards=true`: criar boards remotos)
- [ ] 2.2. Reescrever `sync()` para o fluxo "projeto já existe" (com snapshot.json): checar mtime do pipe.yml, se diferente → atualizar estrutura local e remota (se `create-remote-boards=true`), atualizar `last_sync`, chamar sync de issues
- [ ] 2.3. No fluxo inicial, popular o cache (project_id, field_id, options) para cada board no snapshot — economiza chamadas nos loops subsequentes

### Fase 3 — Sincronização por Virada de Dia

- [ ] 3.1. Mover lógica de `_should_full_sync` para função separada e documentada
- [ ] 3.2. Na virada de dia: se `create-remote-boards=true`, atualizar estrutura de boards remotos
- [ ] 3.3. Na virada de dia: buscar lista completa de items de cada board (1 query GraphQL por board), comparar com snapshot → marcar `b-new` ou `b-del`
- [ ] 3.4. Atualizar `last_sync` para datetime atual

### Fase 4 — Sincronização de Issues (reescrita de `issues.py`)

#### Etapa 1: Local → Snapshot

- [ ] 4.1. Reescrever scan de diretórios: para cada `<id>-<slug>.md` em `.pipe/boards/**`:
  - Se existe local e não no snapshot → status `l-new`
  - Se existe no snapshot com status `ok` e não local → status `l-del`
  - Se existe em ambos e `l-time` < mtime do arquivo → checar coluna e atualizar, status `l-sync`
- [ ] 4.2. Na detecção de movimentação (coluna diferente): atualizar `column`, `path` no snapshot; tratar órfãos (history=remover, write=mover/mesclar)
- [ ] 4.3. Remover toda referência a status `l-mv` — qualquer mudança local (body, coluna, write) unifica em `l-sync`

#### Etapa 2: Snapshot → GitHub

- [ ] 4.4. Para cada issue com status `l-sync`:
  - Se coluna no board ≠ column no snapshot → `move_card` (1 mutation com cache)
  - Se body local ≠ body remoto → `update_issue_body` (1 REST call)
  - Se write preenchido → `post_comment` + limpar write (1 REST call)
  - Reconstruir history local
  - Atualizar `b-time` com updatedAt retornado
  - Status → `ok`
- [ ] 4.5. Para cada issue com status `l-new` (identificadas por `id=0` no snapshot — agentes criam arquivos como `0-slug.md`):
  - Criar issue no GitHub (`create_issue`) → retorna number
  - Adicionar ao project (`add_issue_to_project`) → retorna item_id, cachear
  - Mover para coluna correta (`move_card` usando item_id cacheado)
  - Recriar arquivo com padrão correto
  - Status → `ok`
- [ ] 4.6. Para cada issue com status `l-del` (somente se `allow-del-remote-issue=true`):
  - Postar comentário "Issue removida via agent"
  - Fechar issue no GitHub
  - Remover do snapshot
- [ ] 4.7. Se `allow-del-remote-issue=false` e existe `l-del`: apenas remover do snapshot (issue permanece aberta no GitHub)

#### Etapa 3: GitHub → Snapshot

- [ ] 4.8. Buscar issues modificadas: usar `gh issue list --search "updated:>=<last_sync_date>"` (REST, 1 chamada) para obter lista de numbers modificados
- [ ] 4.9. Para cada issue modificada com `b-time` mais antigo que `updatedAt` do GitHub:
  - Status → `b-sync`
  - Se body remoto ≠ body local → atualizar body local
  - Recriar/atualizar history local
  - Recriar write em branco
  - Se coluna remota ≠ column no snapshot E status anterior era `ok` → mover arquivos locais para novo diretório, atualizar paths
  - Atualizar `b-time`, status → `ok`
- [ ] 4.10. Detectar issues novas no board (existem no board mas não no snapshot) → status `b-new`, preencher dados

#### Etapa 4: Remoção de Resíduos

- [ ] 4.11. Para cada issue com status `b-del`: remover 3 arquivos locais, remover do snapshot
- [ ] 4.12. Para cada issue com status `b-new`: criar 3 arquivos locais (slug, history, write), status → `ok`

### Fase 5 — Integração com `__main__.py`

- [ ] 5.1. Atualizar o loop principal para chamar a sync de issues reescrita
- [ ] 5.2. Remover chamada a `fix_issues()` (não será mais necessário com a nova lógica)
- [ ] 5.3. Garantir que `sync()` (fase 2) rode apenas uma vez ao iniciar
- [ ] 5.4. Garantir que virada de dia (fase 3) seja verificada a cada iteração do loop

### Fase 6 — Testes e Validação

- [ ] 6.1. Criar testes unitários para a nova lógica de detecção (etapa 1)
- [ ] 6.2. Criar testes unitários para as ações de cada etapa (2, 3, 4)
- [ ] 6.3. Criar testes de integração simulando ciclo completo (mock do gh CLI)
- [ ] 6.4. Testar cenários de conflito: movimentação simultânea local+remota
- [ ] 6.5. Testar cenário de rate limit: verificar que o sistema pula graciosamente
- [ ] 6.6. Medir consumo de API antes/depois (comparar chamadas por ciclo)

---

## Estimativa de Consumo de API (por ciclo de sync)

### Antes (código atual)
| Operação | Chamadas/ciclo (5 boards, 20 issues) |
|----------|--------------------------------------|
| resolve_owner | 5 (1 por board) |
| list_projects | 5 |
| item-list (todos items) | 5 |
| issue list updated | 1 |
| issue list created_at | 1 |
| Por movimentação (move_card) | 3-4 cada |
| **Total estimado** | ~25 + 4×moves |

### Depois (com cache)
| Operação | Chamadas/ciclo (5 boards, 20 issues) |
|----------|--------------------------------------|
| fetch_board_items_graphql | 5 (1 query por board, usa cache de metadata) |
| issue list updated | 1 |
| Por movimentação | 1 (só mutation, item_id do cache) |
| **Total estimado** | ~6 + 1×moves |

**Redução**: ~75% menos chamadas API por ciclo. Mutations com 1s de intervalo entre si.

---

## Ordem de Execução Recomendada

1. Fase 0 (preparação) — pré-requisito para tudo
2. Fase 1 (github.py) — pode ser testada isoladamente
3. Fase 4 (issues.py reescrita) — depende de Fase 0 e 1
4. Fase 2 e 3 (sync.py) — depende de Fase 1
5. Fase 5 (integração) — depende de todas
6. Fase 6 (testes) — em paralelo com implementação
