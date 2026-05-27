Status: approved
Owner: engineering-agent
Last updated: 2026-05-27

## Inputs
- docs/01-requirements/meeting-01.md
- docs/02-architecture/overview.md
- docs/02-architecture/adr-001-linguagem-runtime.md
- docs/02-architecture/constraints.md

## Descrição

Criar a estrutura de diretórios e arquivos base do projeto Python. Inclui o layout de `src/`, arquivos de entrada (`__main__.py`, `__init__.py` por módulo), `pyproject.toml` com metadados mínimos e `config/project.json` com valores padrão.

## Tipo
- infra

## Escopo técnico

- Criar `src/orchestrator/__init__.py`
- Criar `src/agents/__init__.py`
- Criar `src/integrations/__init__.py`
- Criar `src/integrations/github/__init__.py`
- Criar `src/integrations/git/__init__.py`
- Criar `src/metrics/__init__.py`
- Criar `src/config/__init__.py`
- Criar `src/__main__.py` com entry point mínimo (imprime versão e sai)
- Criar `pyproject.toml` com `[project]` name, version (0.1.0), requires-python = ">=3.11"
- Criar `config/project.json` com valores padrão: repo, gitflow (branch_base, prefixes), board (columns, labels), agents_sequence
- Criar `state.json` vazio com estrutura inicial: `{"current_feature": null, "current_step": null, "status": "idle"}`
- Criar `.gitignore` cobrindo `__pycache__`, `*.pyc`, `metrics.db`, `.env`

## Fora de escopo

- Implementação de qualquer lógica de negócio
- Testes unitários (não há lógica a testar)
- Criação do `metrics.db` (criado em runtime pelo módulo metrics)

## Critério de aceite (DoD)

- [ ] Estrutura de diretórios corresponde exatamente ao definido em `meeting-01.md`
- [ ] `python -m src` executa sem erro e imprime versão
- [ ] `pyproject.toml` válido com `requires-python = ">=3.11"`
- [ ] `config/project.json` carregável como JSON válido com todos os campos padrão presentes
- [ ] `state.json` existe com estrutura `{"current_feature": null, "current_step": null, "status": "idle"}`
- [ ] `.gitignore` cobre `metrics.db` e `__pycache__`

## Dependências

- Nenhuma

## Ordem sugerida

1 — primeira tarefa a executar; todas as demais dependem desta estrutura
