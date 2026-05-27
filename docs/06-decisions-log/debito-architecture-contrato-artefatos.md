Status: open
Owner: architecture-agent
Last updated: 2026-05-27

## Inputs
- docs/agents/context.md
- docs/agents/*.md
- docs/02-architecture/overview.md

## Descrição

Nenhum documento define de forma centralizada e autoritativa:

1. **Onde cada agente lê seus artefatos de entrada** — os input contracts existem por agente, mas estão dispersos em `docs/agents/<role>.md` e não são verificáveis pelo orquestrador
2. **Onde cada agente deve salvar seus artefatos de saída** — paths concretos não estão padronizados; cada agente infere o diretório pelo contexto
3. **O layout obrigatório de cada artefato** — o padrão de documento em `context.md` define apenas o cabeçalho; a estrutura interna de cada tipo de artefato (user story, ADR, task breakdown, caso de teste, etc.) não tem schema formal

Consequências diretas:
- O orquestrador não consegue verificar se um artefato foi produzido sem conhecer o path esperado
- Um agente pode salvar em path incorreto sem que o erro seja detectado antes da próxima etapa
- Agentes downstream podem falhar silenciosamente ao tentar ler artefatos ausentes ou com estrutura inesperada

## Decisão necessária

Criar um **artefato de contrato de artefatos** (ex: `docs/02-architecture/artifact-map.md`) que defina para cada agente:

- Diretório de leitura (inputs)
- Diretório de escrita (outputs)
- Nome de arquivo esperado (padrão ou template)
- Campos obrigatórios do layout interno

Este mapa deve ser a fonte de verdade consumida pelo orquestrador para verificar pré e pós-condições de cada etapa.

## Impacto

Sem este contrato:
- O orquestrador (task07+) não pode validar automaticamente se uma etapa foi concluída corretamente
- Erros de path só são descobertos na etapa seguinte, aumentando retrabalho
- Novos agentes adicionados à sequência não têm referência clara de onde atuar

## Responsável pela resolução

architecture-agent

## Bloqueia etapa?

Não bloqueia a v1 em execução manual. Bloqueia a implementação de validação automática de artefatos no orquestrador (pós task07).
