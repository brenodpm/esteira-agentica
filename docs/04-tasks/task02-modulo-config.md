Status: approved
Owner: engineering-agent
Last updated: 2026-05-27

## Inputs
- docs/02-architecture/cmp-config.md
- docs/02-architecture/overview.md
- docs/02-architecture/adr-001-linguagem-runtime.md
- docs/04-tasks/task01-estrutura-projeto.md

## Descrição

Implementar o módulo `src/config/` responsável por carregar e validar o arquivo `config/project.json`, aplicar valores padrão para campos ausentes e expor uma interface tipada para os demais módulos.

## Tipo
- dev

## Escopo técnico

- Implementar `src/config/loader.py`:
  - Função `load(path: str | Path = "config/project.json") -> dict` que lê e valida o JSON
  - Aplicar defaults para campos ausentes: `repo`, `gitflow.branch_base = "develop"`, `gitflow.prefixes = {"feature": "feature/", "fix": "fix/", "release": "release/", "hotfix": "hotfix/"}`, `board.columns = ["Backlog", "In Progress", "Done"]`, `board.labels = {}`, `agents_sequence = [...]`
  - Lançar `ValueError` com mensagem clara se campo obrigatório (`repo`) estiver ausente
- Atualizar `src/config/__init__.py` para exportar `load`
- Criar `tests/test_config.py` com casos:
  - Carrega JSON válido completo
  - Aplica defaults quando campos opcionais ausentes
  - Lança `ValueError` quando `repo` ausente

## Fora de escopo

- Validação de conectividade com o GitHub
- Criação ou edição do `config/project.json`
- Suporte a formatos além de JSON (YAML, TOML)

## Critério de aceite (DoD)

- [ ] `load()` retorna dict com todos os campos (incluindo defaults aplicados)
- [ ] `load()` lança `ValueError` se `repo` ausente
- [ ] Todos os testes em `tests/test_config.py` passam
- [ ] Sem imports externos (apenas `json`, `pathlib` da stdlib)

## Dependências

- task01 (estrutura de projeto)

## Ordem sugerida

2 — base para todos os módulos que precisam de configuração
