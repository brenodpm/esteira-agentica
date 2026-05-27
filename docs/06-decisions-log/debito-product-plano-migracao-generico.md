Status: open
Owner: product-agent
Last updated: 2026-05-27

## Inputs
- docs/00-product/vision.md
- docs/00-product/problem-space.md

## Descrição

Criar um plano de migração genérico para times que já usam outro método de desenvolvimento (manual, outra esteira, CI/CD tradicional, etc.) e querem adotar esta esteira.

Escopo esperado:
- Diagnóstico do estado atual (o que o time já tem: board, git, agentes, etc.)
- Mapeamento do que precisa ser configurado para usar a esteira
- Passos incrementais de adoção — não exige migração big-bang
- Guia de configuração do `config/` por projeto
- Checklist de pré-requisitos (gh CLI, git, Kiro CLI, GitHub repo)

> **Incerteza:** o nível de variação entre os contextos de adotantes externos é desconhecido. O plano deve ser validado com pelo menos um caso real antes de ser considerado genérico de fato.

## Impacto

Sem isso, o projeto é adotável apenas por quem já conhece a estrutura internamente — limita o alcance do produto.

## Responsável pela resolução

product-agent (estrutura do plano) + requirements-agent (detalhamento dos casos de uso de migração)

## Bloqueia etapa?

Não — relevante após a v1 estar estável e documentada.
