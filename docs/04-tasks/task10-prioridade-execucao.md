Status: approved
Owner: engineering-agent
Last updated: 2026-05-27

## Inputs
- docs/02-architecture/adr-006-prioridade-execucao-tasks.md
- docs/02-architecture/overview.md
- docs/04-tasks/task07-modulo-orchestrator.md
- docs/04-tasks/task09-mecanismo-bloqueio.md

## Descrição

Substituir a seleção simples de próxima issue por uma função de prioridade que respeita a hierarquia definida no ADR-006: sub-issues em andamento > sub-issues no backlog do milestone corrente > issues do milestone corrente > novo milestone.

## Tipo
- dev

## Escopo técnico

- Implementar `src/orchestrator/priority.py`:
  - `select_next(config: dict, state: dict) -> dict | None` — retorna a próxima issue a processar seguindo a hierarquia:
    1. Sub-issues com label `in-progress` do milestone corrente (mais antiga primeiro)
    2. Sub-issues no backlog do milestone corrente sem label `blocked` ou `needs-human` (mais antiga primeiro)
    3. Issues do milestone corrente sem sub-issues pendentes, sem `blocked` ou `needs-human` (mais antiga primeiro)
    4. Issues do próximo milestone (apenas se milestone corrente não tiver issues abertas)
    - Retorna `None` se não houver nenhuma issue disponível em nenhum nível
  - `get_current_milestone(config: dict, state: dict) -> str | None` — retorna o milestone corrente do estado ou o primeiro milestone com issues abertas

- Substituir chamada a `github.get_next_issue()` em `src/orchestrator/runner.py` por `priority.select_next()`

- Atualizar `src/orchestrator/__init__.py` para exportar `priority`

- Criar `tests/test_priority.py` cobrindo:
  - Sub-issue em andamento tem prioridade sobre issue nova
  - Sub-issue no backlog tem prioridade sobre issue sem sub-issues
  - Issue do milestone corrente tem prioridade sobre issue de milestone futuro
  - Novo milestone só é iniciado quando milestone corrente está vazio
  - Issues com `blocked` são ignoradas em todos os níveis
  - Empate dentro do mesmo nível: mais antiga primeiro (menor `created_at`)

## Fora de escopo

- Prioridade manual por label de urgência (v2)
- Paralelismo entre issues (débito documentado)
- Reordenação manual do backlog pelo usuário via board (respeitada implicitamente pela ordem de criação)

## Critério de aceite (DoD)

- [ ] `select_next` nunca retorna issue com label `blocked` ou `needs-human`
- [ ] Hierarquia dos 4 níveis respeitada em todos os cenários de teste
- [ ] Empate resolvido por `created_at` ascendente
- [ ] Novo milestone só iniciado com milestone corrente sem issues abertas
- [ ] Todos os testes em `tests/test_priority.py` passam com mocks

## Dependências

- task07 (orchestrator base — `run_once` usa `get_next_issue`)
- task09 (mecanismo de bloqueio — labels `blocked`/`needs-human` já implementadas)
- task03 (integrations/github — consultas de issues por milestone e sub-issues)

## Ordem sugerida

10 — refinamento do orchestrator; depende do mecanismo de bloqueio para filtrar corretamente
