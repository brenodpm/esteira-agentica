Status: done
Owner: engineering-agent
Last updated: 2026-05-27

## Inputs
- docs/02-architecture/cmp-integration-git.md
- docs/02-architecture/overview.md
- docs/gitflow.md
- docs/04-tasks/task02-modulo-config.md

## Descrição

Implementar o módulo `src/integrations/git/` que abstrai operações de versionamento local via `git` CLI. Cobre criação de branches seguindo o gitflow configurado, commits com mensagem padronizada e push para o remote.

## Tipo
- dev

## Escopo técnico

- Implementar `src/integrations/git/client.py` com as funções:
  - `create_branch(config: dict, branch_type: str, name: str) -> str` — cria e faz checkout de branch com prefixo do gitflow (ex: `feature/nome`), a partir de `config.gitflow.branch_base`; retorna o nome completo da branch
  - `commit(config: dict, message: str, files: list[str] | None = None) -> None` — faz `git add` nos arquivos listados (ou `git add -A` se None) e `git commit -m message`
  - `push(branch: str) -> None` — executa `git push -u origin <branch>`
  - `current_branch() -> str` — retorna o nome da branch atual via `git rev-parse --abbrev-ref HEAD`
- Todas as funções invocam `git` via `subprocess.run` com `check=True`; erros propagam como `RuntimeError` com stderr
- Atualizar `src/integrations/git/__init__.py` para exportar todas as funções
- Criar `tests/test_git.py` com mocks de `subprocess.run` cobrindo:
  - `create_branch` monta nome correto com prefixo do gitflow
  - `create_branch` usa `branch_base` da config como ponto de partida
  - `commit` com `files=None` executa `git add -A`
  - `commit` com lista de arquivos executa `git add` apenas nos arquivos listados

## Fora de escopo

- Operações de merge, rebase ou cherry-pick
- Abertura de PR (responsabilidade de `integrations/github`)
- Configuração de credenciais git

## Critério de aceite (DoD)

- [ ] `create_branch` respeita prefixos definidos em `config.gitflow.prefixes`
- [ ] `create_branch` parte sempre de `config.gitflow.branch_base`
- [ ] Erros do `git` CLI propagam como `RuntimeError` com mensagem legível
- [ ] Todos os testes em `tests/test_git.py` passam com mocks

## Dependências

- task02 (módulo config — fornece gitflow)

## Ordem sugerida

4 — necessário para orchestrator criar branches ao iniciar features
