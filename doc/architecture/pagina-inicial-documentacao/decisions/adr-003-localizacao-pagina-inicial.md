# ADR-003 — Localização da Página Inicial

Status: accepted
Owner: architecture
Last updated: 2024-06-14

## Inputs
- Convenções de documentação de projetos
- Estrutura existente com `/docs`

## Contexto
A página inicial pode ficar no root do projeto (README.md) ou dentro da estrutura de documentação (/docs/index.md).

## Decisão
Criar `/docs/README.md` como página inicial da documentação, mantendo o `README.md` do root focado no projeto em si.

## Justificativa
- Separação clara entre documentação do projeto e do código
- Permite evolução independente de cada tipo de documentação
- Facilita navegação em ferramentas de documentação

## Consequências
- Positivas: Segregação clara de responsabilidades
- Negativas: Possível duplicação de links de entrada
- Riscos: Usuário pode não encontrar a documentação completa
