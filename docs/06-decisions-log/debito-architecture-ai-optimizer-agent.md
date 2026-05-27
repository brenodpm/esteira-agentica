Status: open
Owner: architecture-agent
Last updated: 2026-05-26

## Inputs
- docs/00-product/epicos.md
- docs/02-architecture/adr-003-persistencia-estado-metricas.md

## Descrição

Avaliar e documentar a criação de um novo agente especialista em IAs — provisoriamente chamado de **AI Optimizer Agent** — cuja função é, ao final de cada ciclo (equivalente a uma sprint), revisar as métricas coletadas da esteira e otimizar os demais agentes com base nas melhores práticas da IA utilizada.

Escopo esperado do agente:
- Lê métricas do ciclo (custo em tokens, tempo de execução, taxa de retrabalho, qualidade de resultado)
- Identifica agentes com pior desempenho
- Aplica ou propõe ajustes nos prompts/contextos dos agentes com base nas melhores práticas da IA em uso
- Objetivos de otimização: custo, performance, qualidade de resultado e outros identificados na análise

Analogia funcional: uma sprint review focada em otimização dos agentes, não do produto.

> **Incerteza:** a viabilidade de otimização automática de prompts depende das capacidades da IA utilizada e do nível de acesso aos parâmetros dos agentes. Precisa ser amadurecida pelo product agent antes de virar épico.

## Impacto

Sem este agente, a otimização dos demais agentes é manual e não sistemática. O custo em tokens tende a crescer sem controle ao longo dos ciclos.

## Responsável pela resolução

product-agent

## Bloqueia etapa?

Não — é evolução futura, não bloqueia a v1.
