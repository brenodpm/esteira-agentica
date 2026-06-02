Status: draft
Owner: product-agent
Issue: #22
Last updated: 2026-06-02

## Inputs
- src/orchestrator/runner.py
- esteira.yml
- logs/esteira-2026-06-02.jsonl

## Problema
Após o agente concluir sua execução e abrir o PR, o runner move o card para a coluna corrente (ex: "Análise de Negócio") em vez de avançá-lo para a coluna de aprovação seguinte (ex: "Aprovação Negócio"). O humano precisa mover manualmente o card para a coluna correta, quebrando a automação e gerando confusão sobre o estado real do board.

## Solução
Ao concluir a execução de um agente com `git_commit: true`, o runner deve mover o card diretamente para a coluna definida em `change.advance` da coluna atual — que representa a fila de aprovação — em vez de manter o card na coluna do agente.

## Público-alvo
Usuários da esteira que acompanham o progresso via board do GitHub Projects.

## Proposta de valor
O board reflete fielmente o estado real do processo: após o agente terminar, o card aparece imediatamente na coluna de aprovação correta, sem intervenção manual.

## Métricas de sucesso
- Zero movimentações manuais necessárias após execução de agente com PR aberto
- Card sempre na coluna correspondente ao estado em `state.json`
