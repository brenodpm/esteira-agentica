Status: approved
Owner: engineering-agent
Last updated: 2026-05-27T14:14-03:00

## Inputs
- docs/02-architecture/cmp-agents.md
- docs/02-architecture/overview.md
- docs/02-architecture/adr-001-linguagem-runtime.md
- docs/agents/context.md
- docs/04-tasks/task01-estrutura-projeto.md

## Descrição

Implementar o módulo `src/agents/` responsável por invocar agentes via Kiro CLI (`kiro chat`) como subprocesso, capturar a saída e retornar resultado estruturado. Cada agente recebe um contexto mínimo e produz um artefato.

## Tipo
- dev

## Escopo técnico

- Implementar `src/agents/runner.py` com:
  - `run(role: str, context_files: list[str], prompt: str, timeout_s: int = 300) -> dict` — invoca `kiro chat --agent <role>` via `subprocess.run`, passando `prompt` via stdin; retorna `{"output": str, "tokens_in": int | None, "tokens_out": int | None, "duration_s": float}`
    - `context_files` são passados como flags `--context <path>` se o Kiro CLI suportar; caso contrário, concatenados no início do prompt
    - `tokens_in` e `tokens_out` extraídos do stdout/stderr se Kiro CLI os expuser; caso contrário, `None`
    - Timeout lança `TimeoutError` com mensagem indicando o agente e o tempo limite
    - Código de saída não-zero lança `RuntimeError` com stderr
  - `AGENT_ROLES: list[str]` — lista dos papéis válidos: `["product", "requirements", "architecture", "engineering", "quality", "operations"]`
- Atualizar `src/agents/__init__.py` para exportar `run` e `AGENT_ROLES`
- Criar `tests/test_agents.py` com mocks de `subprocess.run` cobrindo:
  - `run` retorna dict com `output` e `duration_s` preenchidos
  - `run` lança `TimeoutError` quando processo excede timeout
  - `run` lança `RuntimeError` quando código de saída não-zero

## Fora de escopo

- Lógica de negócio de cada agente (definida nos prompts em `docs/agents/`)
- Parsing do artefato produzido (responsabilidade do orchestrator)
- Comunicação direta entre agentes

## Critério de aceite (DoD)

- [ ] `run` invoca `kiro` via `subprocess` sem dependências externas
- [ ] `tokens_in`/`tokens_out` retornam `None` quando não disponíveis (sem erro)
- [ ] Timeout e erro de processo propagam com mensagens claras
- [ ] Todos os testes em `tests/test_agents.py` passam com mocks

## Dependências

- task01 (estrutura de projeto)

## Ordem sugerida

6 — independente dos módulos de integração; pode ser desenvolvido em paralelo com task03, task04 e task05
