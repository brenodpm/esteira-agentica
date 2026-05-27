Status: approved
Owner: engineering-agent
Last updated: 2026-05-27T14:50-03:00

## Inputs
- docs/02-architecture/overview.md
- docs/02-architecture/adr-002-mecanismo-orquestracao.md
- docs/02-architecture/adr-005-interacao-humano-issues.md
- docs/04-tasks/task07-modulo-orchestrator.md

## Descrição

Adicionar ao orquestrador o gate de aprovação humana entre etapas. Após cada execução de agente, o orquestrador posta o resultado na issue, atualiza o estado para `"awaiting_approval"` e aguarda label `approved` ou `rejected` antes de avançar. Em caso de rejeição, retorna ao mesmo agente com contexto de retrabalho.

## Tipo
- dev

## Escopo técnico

- Adicionar em `src/orchestrator/runner.py`:
  - Após `agents.run()`, postar output do agente como comentário na issue via `github.post_comment()`
  - Salvar estado com `status = "awaiting_approval"` e `current_step` mantido
  - Em `run_once`: se `status == "awaiting_approval"`, verificar aprovação via `github.get_approval_status()`:
    - `"approved"` → remover label `approved`, avançar `current_step`, setar `status = "idle"`
    - `"rejected"` → remover label `rejected`, setar `rework = True` no estado, manter `current_step` (re-executa o mesmo agente na próxima iteração)
    - `"pending"` → retornar sem alterar estado (aguarda próxima iteração do loop)
  - Ao re-executar agente com `rework = True`: passar flag para `metrics.record(rework=True)` e incluir comentário de rejeição no contexto do agente

- Atualizar `src/orchestrator/state.py` para incluir campo `rework: bool = False` no estado

- Criar `tests/test_gate.py` cobrindo:
  - Estado `"awaiting_approval"` com status `"pending"` → nenhuma ação, estado inalterado
  - Estado `"awaiting_approval"` com status `"approved"` → `current_step` avança, `status` volta a `"idle"`
  - Estado `"awaiting_approval"` com status `"rejected"` → `current_step` mantido, `rework = True`
  - Re-execução com `rework = True` chama `metrics.record` com `rework=True`

## Fora de escopo

- Notificação ativa ao usuário (toda comunicação é pull via GitHub)
- SLA de aprovação ou escalada por timeout (débito futuro)
- Aprovação automática por qualquer critério

## Critério de aceite (DoD)

- [ ] Orquestrador não avança etapa sem label `approved` na issue
- [ ] Rejeição re-executa o mesmo agente com `rework=True` registrado em metrics
- [ ] Estado `"awaiting_approval"` persiste entre reinicializações do processo
- [ ] Todos os testes em `tests/test_gate.py` passam com mocks

## Dependências

- task07 (orchestrator base)
- task03 (integrations/github — `post_comment`, `get_approval_status`, `remove_label`)

## Ordem sugerida

8 — extensão do orchestrator; depende do loop base estar funcionando
