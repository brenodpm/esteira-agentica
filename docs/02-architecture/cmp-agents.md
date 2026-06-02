Status: approved
Owner: architecture-agent
Last updated: 2026-05-26

## Inputs
- docs/02-architecture/overview.md
- docs/agents/context.md

## Responsabilidade

Módulos individuais de cada papel da esteira (product, requirements, architecture, engineering, quality, operations). Cada agente recebe um contexto mínimo, executa via Kiro CLI e produz um artefato bem delimitado. Não se comunicam entre si — toda coordenação passa pelo `orchestrator`.

## Entradas

- Contexto mínimo necessário para a etapa (artefatos da etapa anterior, issue corrente)
- Prompt específico do papel (definido em `docs/agents/<role>.md`)

## Saídas

- Artefato produzido (arquivo em `docs/`) ou ação executada
- Contagem de tokens consumidos (capturada pelo `orchestrator` para repasse ao `metrics`)

## Dependências

- Nenhuma dependência direta entre agentes
- Invocados pelo `orchestrator` via `subprocess` (Kiro CLI)
- Leem artefatos de `docs/` conforme definido no input contract de cada papel
