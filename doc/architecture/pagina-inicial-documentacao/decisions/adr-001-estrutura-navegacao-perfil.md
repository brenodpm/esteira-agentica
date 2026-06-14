# ADR-001 — Estrutura de Navegação por Perfil de Usuário

Status: accepted
Owner: architecture
Last updated: 2024-06-14

## Inputs
- Critérios de aceitação da story
- Análise de usuários (iniciante, avançado, desenvolvedor)

## Contexto
A documentação precisa atender diferentes perfis de usuário com necessidades distintas. Cada perfil tem pontos de entrada e fluxos específicos.

## Decisão
Organizar página inicial em seções dedicadas por perfil:
- **Iniciantes**: Instalação, primeiros passos, conceitos básicos
- **Usuários Avançados**: Configuração, casos de uso específicos, troubleshooting
- **Desenvolvedores**: Arquitetura, extensões, contribuição

## Justificativa
- Reduz tempo de busca por informação relevante
- Evita sobrecarga cognitiva com informação irrelevante
- Facilita manutenção com segregação clara

## Consequências
- Positivas: Navegação mais eficiente, melhor experiência do usuário
- Negativas: Possível duplicação conceitual entre seções
- Riscos: Usuário pode não se identificar com perfil correto
