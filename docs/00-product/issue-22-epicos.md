Status: draft
Owner: product-agent
Issue: #22
Last updated: 2026-06-02

## Inputs
- docs/00-product/issue-22-vision.md
- docs/00-product/issue-22-problem-space.md

---

## Épico: Consistência do Board com o State

**Objetivo:** Garantir que a posição do card no board reflita sempre o estado real registrado em `state.json`, sem necessidade de intervenção manual.

**Escopo:**
- Corrigir a chamada `github.move_card` após execução de agente com PR aberto: mover para a coluna `advance` (aprovação) em vez da coluna atual do agente
- Validar que o card termina na coluna correta em todos os cenários: agente com `git_commit: true`, agente sem commit, rejeição, e conclusão

**Fora de escopo:** Reconciliação retroativa de cards já movidos manualmente, sincronização bidirecional board → state.

---

## Épico: Cobertura de Testes do Runner

**Objetivo:** Evitar regressão na lógica de movimentação do board com testes automatizados.

**Escopo:**
- Adicionar caso de teste que verifica para qual coluna o card é movido após execução do agente com `git_commit: true`
- Cobrir o caminho de aprovação e rejeição

**Fora de escopo:** Testes de integração com GitHub Projects real.
