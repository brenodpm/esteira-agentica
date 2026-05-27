Status: approved
Owner: engineering-agent
Last updated: 2026-05-27T15:02-03:00

## Inputs
- docs/02-architecture/adr-004-mecanismo-bloqueio-tasks.md
- docs/02-architecture/adr-005-interacao-humano-issues.md
- docs/02-architecture/overview.md
- docs/04-tasks/task07-modulo-orchestrator.md
- docs/04-tasks/task08-gate-aprovacao-humana.md

## Descrição

Adicionar ao orquestrador o mecanismo de bloqueio de tasks. Quando um agente detecta dependência bloqueante, cria issue bloqueante no GitHub, adiciona label `blocked` na issue corrente e o orquestrador pula para a próxima issue disponível. Ao concluir a issue bloqueante, o orquestrador remove a label `blocked` da dependente e a recoloca no backlog.

## Tipo
- dev

## Escopo técnico

- Adicionar em `src/orchestrator/runner.py`:
  - Em `run_once`: ao selecionar próxima issue via `github.get_next_issue()`, garantir que issues com label `blocked` são excluídas (já coberto em task03, verificar)
  - Após conclusão de cada issue: chamar `_unblock_dependents(config, issue_number)` que:
    1. Busca issues com label `blocked` que referenciam a issue concluída no corpo ou em comentários
    2. Remove label `blocked` dessas issues via `github.remove_label()`
    3. Move card de volta para "Backlog" via `github.move_card()`
  - Detectar ciclo de bloqueio mútuo: se todas as issues disponíveis têm label `blocked`, criar issue com label `needs-human` descrevendo o ciclo e parar o loop

- Implementar `src/orchestrator/blocker.py`:
  - `create_blocker(config: dict, blocked_issue: int, title: str, body: str, needs_human: bool = False) -> int` — cria issue bloqueante, adiciona label `blocked` na issue corrente, retorna número da issue criada
  - `unblock_dependents(config: dict, resolved_issue: int) -> list[int]` — encontra e desbloqueia issues dependentes; retorna lista de números desbloqueados
  - `detect_deadlock(config: dict) -> bool` — retorna True se todas as issues disponíveis estão bloqueadas

- Atualizar `src/orchestrator/__init__.py` para exportar `blocker`

- Criar `tests/test_blocker.py` cobrindo:
  - `create_blocker` adiciona label `blocked` na issue corrente e cria nova issue
  - `create_blocker` com `needs_human=True` adiciona label `needs-human` na issue criada
  - `unblock_dependents` remove label `blocked` de issues que referenciam a issue resolvida
  - `detect_deadlock` retorna True quando todas as issues têm label `blocked`
  - `detect_deadlock` retorna False quando há pelo menos uma issue sem `blocked`

## Fora de escopo

- Resolução automática de bloqueios humanos (`needs-human`)
- Topologia de dependências pré-definida (descoberta em runtime via labels)
- SLA de resolução de bloqueios

## Critério de aceite (DoD)

- [ ] Issues com label `blocked` nunca são selecionadas pelo orquestrador
- [ ] Conclusão de issue bloqueante desbloqueia automaticamente as dependentes
- [ ] Ciclo de bloqueio mútuo gera issue `needs-human` e para o loop
- [ ] Todos os testes em `tests/test_blocker.py` passam com mocks

## Dependências

- task07 (orchestrator base)
- task08 (gate de aprovação — define quando uma issue é "concluída")
- task03 (integrations/github — `create_issue`, `add_label`, `remove_label`, `move_card`)

## Ordem sugerida

9 — extensão do orchestrator após gate de aprovação estar implementado
