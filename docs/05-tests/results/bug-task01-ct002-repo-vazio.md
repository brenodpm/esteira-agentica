Status: resolved
Owner: quality-agent
Last updated: 2026-05-27

## Inputs
- docs/05-tests/tc-task01-estrutura-projeto.md — CT-002
- docs/04-tasks/task01-estrutura-projeto.md

## Descrição
`python -m src` falha com `ValueError` porque `config/project.json` tem `"repo": ""` (string vazia), e `load_config()` rejeita valores vazios para o campo obrigatório `repo`.

## Passos para reproduzir
1. Clonar o repositório
2. Na raiz do projeto, executar `python -m src`

## Resultado esperado
- Exit code 0
- Saída contém a versão do projeto (ex: `0.1.0`)

## Resultado obtido
- Exit code 1
- Traceback:
  ```
  File "src/config/loader.py", line 31, in load
    raise ValueError("Campo obrigatório 'repo' ausente ou vazio em config")
  ValueError: Campo obrigatório 'repo' ausente ou vazio em config
  ```

## Severidade
high

## Violação
- requisito (task01 — entry point mínimo deve executar sem erro)
