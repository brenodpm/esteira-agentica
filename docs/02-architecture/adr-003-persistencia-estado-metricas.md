Status: accepted
Owner: architecture-agent
Last updated: 2026-05-26

## Inputs
- docs/00-product/vision.md (métricas de sucesso)
- docs/00-product/epicos.md (épico: Coleta de Métricas)
- docs/02-architecture/constraints.md
- docs/02-architecture/adr-002-mecanismo-orquestracao.md

## Contexto

O sistema precisa persistir dois tipos de dados:

1. **Estado da orquestração** — etapa atual, feature em andamento, resultado de cada agente, histórico de gates. Precisa sobreviver a reinicializações e ser recuperável.
2. **Métricas de execução** — custo em tokens por agente e por feature (P1), tempo de execução por etapa, taxa de retrabalho. Precisa ser consultável e auditável.

As opções consideradas foram:

- **JSON em arquivo** — simples, legível, versionável
- **SQLite** — consultável via SQL, sem servidor, stdlib Python
- **Ambos** — JSON para estado (legível/versionável), SQLite para métricas (consultável)

## Decisão

**JSON para estado da orquestração + SQLite para métricas.**

- `state.json` — arquivo único por execução, atualizado a cada transição de estado
- `metrics.db` — banco SQLite local, uma linha por execução de agente com: feature_id, agent, tokens_in, tokens_out, duration_s, rework (bool), timestamp

> **Incerteza — custo em tokens:** a captura de `tokens_in`/`tokens_out` depende do Kiro CLI expor essa informação na saída. Não verificado. A ser confirmado no technical design; se não for viável, o campo fica nulo até solução alternativa ser identificada.

> **Incerteza — alucinação:** detectar alucinação automaticamente não é factível na v1. O campo `hallucination` não será coletado automaticamente. A abordagem viável é o humano sinalizar via label no gate de aprovação; o orquestrador registra a label como evento. A ser amadurecido em versão futura.

## Justificativa

- Estado em JSON é legível sem ferramentas, versionável em git se necessário, e suficiente para o volume (uma feature por vez)
- Métricas em SQLite permitem queries de agregação (custo total por feature, agente mais caro) sem dependências externas — `sqlite3` é stdlib Python
- Separar os dois tipos evita misturar dados operacionais com dados analíticos no mesmo arquivo
- Ambas as opções são zero-dependency e alinhadas com ADR-001

## Consequências

- Positivas: consultas de métricas via SQL sem ferramentas externas; estado auditável; sem servidor de banco de dados
- Negativas: SQLite não é adequado para acesso concorrente (irrelevante — execução single-process)
- Riscos: corrupção do `state.json` em crash durante escrita — mitigado por escrita atômica (write temp + rename)

## Changes
- Removido `hallucination (bool)` do schema como dado coletado automaticamente — não é factível na v1
- Captura de tokens marcada como incerteza — depende de suporte do Kiro CLI, não verificado
- Motivo: não prometer o que não se sabe se pode ser cumprido; incertezas explicitadas para amadurecimento no technical design