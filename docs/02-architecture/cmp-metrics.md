Status: approved
Owner: architecture-agent
Last updated: 2026-05-26

## Inputs
- docs/00-product/vision.md (métricas de sucesso)
- docs/00-product/epicos.md (épico: Coleta de Métricas)
- docs/02-architecture/adr-003-persistencia-estado-metricas.md

## Responsabilidade

Coleta e persiste métricas de execução da esteira. Registra tempo de execução e retrabalho por agente e por feature. Expõe consultas de agregação para auditoria.

> **Incerteza — custo em tokens (P1):** coleta de `tokens_in`/`tokens_out` depende do Kiro CLI expor essa informação. Não verificado — a ser confirmado no technical design.

> **Incerteza — alucinação:** não coletada automaticamente na v1. Evento registrado apenas se humano sinalizar via label no gate de aprovação. A ser amadurecido.

## Entradas

- Dados de execução de cada agente: feature_id, agent, tokens_in (incerto), tokens_out (incerto), duration_s, rework (bool), timestamp
- Fornecidos pelo `orchestrator` ao final de cada execução de agente

## Saídas

- Registro persistido em `metrics.db` (SQLite)
- Consultas de agregação: custo total por feature, custo por agente, agentes com maior taxa de retrabalho

## Dependências

- `sqlite3` (stdlib Python)
- Sem dependência de outros módulos internos
- Chamado exclusivamente pelo `orchestrator`

## Changes
- Tokens marcados como incertos; hallucination removida como coleta automática
- Motivo: alinhamento com ADR-003 revisado