Status: approved
Owner: engineering-agent
Last updated: 2026-05-27

## Inputs
- docs/02-architecture/cmp-orchestrator.md
- docs/02-architecture/overview.md
- docs/02-architecture/adr-002-mecanismo-orquestracao.md
- docs/02-architecture/adr-003-persistencia-estado-metricas.md
- docs/04-tasks/task02-modulo-config.md
- docs/04-tasks/task03-modulo-integrations-github.md
- docs/04-tasks/task04-modulo-integrations-git.md
- docs/04-tasks/task05-modulo-metrics.md
- docs/04-tasks/task06-modulo-agents.md

## Descrição

Implementar o loop principal do orquestrador em `src/orchestrator/`. Responsável por ler o estado atual, selecionar a próxima issue, acionar o agente correto na sequência, persistir o estado a cada transição e registrar métricas. Não inclui gate de aprovação humana (task08) nem mecanismo de bloqueio (task09).

## Tipo
- dev

## Escopo técnico

- Implementar `src/orchestrator/state.py`:
  - `load(path: str | Path = "state.json") -> dict` — lê state.json; retorna estado inicial se arquivo não existir
  - `save(state: dict, path: str | Path = "state.json") -> None` — escrita atômica (write temp + `os.replace`)
  - Estado mínimo: `{"current_feature": null, "current_step": null, "status": "idle", "issue_number": null}`

- Implementar `src/orchestrator/runner.py`:
  - `run_once(config: dict) -> None` — executa um ciclo completo:
    1. Carrega estado via `state.load()`
    2. Se `status == "idle"`: busca próxima issue via `github.get_next_issue()`; se None, retorna (backlog vazio)
    3. Cria branch via `git.create_branch()` se `current_step` é None (início de feature)
    4. Determina próximo agente da sequência (`config.agents_sequence[current_step_index]`)
    5. Invoca agente via `agents.run()`
    6. Registra execução via `metrics.record()`
    7. Salva estado com `current_step` avançado
    8. Move card para "In Progress" via `github.move_card()`
  - `run_loop(config: dict, poll_interval_s: int = 60) -> None` — chama `run_once` em loop com `time.sleep(poll_interval_s)` entre iterações; captura `KeyboardInterrupt` para saída limpa

- Atualizar `src/__main__.py` para chamar `run_loop` com config carregada
- Criar `tests/test_orchestrator.py` com mocks cobrindo:
  - `run_once` retorna sem erro quando backlog vazio
  - `run_once` avança `current_step` após execução bem-sucedida do agente
  - `state.save` usa escrita atômica (verifica uso de arquivo temporário + rename)

## Fora de escopo

- Gate de aprovação humana (task08)
- Mecanismo de bloqueio de tasks (task09)
- Prioridade de execução (task10)

## Critério de aceite (DoD)

- [ ] `state.save` usa escrita atômica (`os.replace`) — sem corrupção em crash
- [ ] `run_once` com backlog vazio retorna sem erro e sem alterar estado
- [ ] `run_once` avança `current_step` e persiste estado após cada agente
- [ ] `run_loop` captura `KeyboardInterrupt` e encerra sem stack trace
- [ ] Todos os testes em `tests/test_orchestrator.py` passam com mocks

## Dependências

- task02 (config)
- task03 (integrations/github)
- task04 (integrations/git)
- task05 (metrics)
- task06 (agents)

## Ordem sugerida

7 — integra todos os módulos anteriores; base para as tasks de gate e bloqueio
