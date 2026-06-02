Status: done
Owner: engineering-agent
Last updated: 2026-05-27

## Inputs
- docs/02-architecture/cmp-integration-github.md
- docs/02-architecture/overview.md
- docs/02-architecture/adr-004-mecanismo-bloqueio-tasks.md
- docs/02-architecture/adr-005-interacao-humano-issues.md
- docs/01-requirements/github-setup.md
- docs/04-tasks/task02-modulo-config.md

## Descrição

Implementar o módulo `src/integrations/github/` que abstrai toda comunicação com a API do GitHub via `gh` CLI. Cobre leitura de issues, movimentação de cards no board, postagem de comentários, detecção de labels e abertura de PRs.

## Tipo
- dev

## Escopo técnico

- Implementar `src/integrations/github/client.py` com as funções:
  - `get_next_issue(config: dict) -> dict | None` — retorna a próxima issue do backlog (sem label `blocked` ou `needs-human`), ordenada por criação mais antiga
  - `get_issue(config: dict, issue_number: int) -> dict` — retorna dados de uma issue específica
  - `post_comment(config: dict, issue_number: int, body: str) -> None` — posta comentário na issue
  - `add_label(config: dict, issue_number: int, label: str) -> None` — adiciona label à issue
  - `remove_label(config: dict, issue_number: int, label: str) -> None` — remove label da issue
  - `move_card(config: dict, issue_number: int, column: str) -> None` — move issue para coluna do board
  - `open_pr(config: dict, title: str, body: str, head: str, base: str) -> dict` — abre PR
  - `create_issue(config: dict, title: str, body: str, labels: list[str]) -> dict` — cria nova issue
  - `get_approval_status(config: dict, issue_number: int) -> str` — retorna `"approved"`, `"rejected"` ou `"pending"` com base nas labels da issue
- Todas as funções invocam `gh` via `subprocess.run` com `check=True`; erros de `gh` propagam como `RuntimeError` com mensagem do stderr
- Atualizar `src/integrations/github/__init__.py` para exportar todas as funções
- Criar `tests/test_github.py` com mocks de `subprocess.run` cobrindo:
  - `get_next_issue` retorna None quando backlog vazio
  - `get_next_issue` pula issues com label `blocked`
  - `get_approval_status` retorna `"approved"` quando label `approved` presente
  - `get_approval_status` retorna `"rejected"` quando label `rejected` presente
  - `get_approval_status` retorna `"pending"` quando nenhuma das duas labels presente

## Fora de escopo

- Autenticação com GitHub (responsabilidade do usuário via `gh auth login`)
- Criação de labels e milestones no repositório (task11)
- Paginação de issues (v1 assume backlog pequeno)

## Critério de aceite (DoD)

- [ ] Todas as funções invocam `gh` via `subprocess` sem dependências externas
- [ ] `get_next_issue` exclui issues com labels `blocked` e `needs-human`
- [ ] `get_approval_status` distingue corretamente os três estados
- [ ] Erros do `gh` CLI propagam como `RuntimeError` com mensagem legível
- [ ] Todos os testes em `tests/test_github.py` passam com mocks

## Dependências

- task02 (módulo config — fornece `repo`, `board.labels`)

## Ordem sugerida

3 — necessário para orchestrator ler backlog e postar resultados
