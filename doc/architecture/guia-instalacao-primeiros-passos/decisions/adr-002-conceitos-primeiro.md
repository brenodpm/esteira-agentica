# ADR-002 — Conceitos antes da instalação

Status: accepted
Owner: architecture
Last updated: 2026-06-22

## Inputs
- Regra de negócio RN-003: Conceitos explicados antes dos passos técnicos
- pipe.yml: estrutura atual de agentes, boards e configurações

## Contexto

Definir se conceitos fundamentais (agentes, boards, pipe.yml, model/effort) devem ser explicados antes ou durante os passos de instalação.

## Decisão

Seção de conceitos deve preceder todas as instruções técnicas.

## Justificativa

- **Reduz confusão:** usuário entende o que está instalando antes de executar
- **Evita suposições:** contexto claro sobre terminologia usada no resto do guia
- **Facilita troubleshooting:** usuário com conceitos claros diagnostica melhor problemas
- **Atende RN-003:** requisito explícito de conceitos antes de técnico
- **Melhora retenção:** aprendizado contextualizado é mais efetivo

## Consequências

- **Positivas:**
  - Menor taxa de abandono durante instalação
  - Redução de perguntas básicas em canais de suporte
  - Base sólida para casos de uso avançados futuros
  
- **Negativas:**
  - Aumenta tempo até primeira execução (reading overhead)
  - Pode frustrar usuários que querem "ir direto ao ponto"
  
- **Riscos:**
  - Se conceitos ficarem muito teóricos, pode desencorajar usuários práticos
  - Necessário balancear profundidade com concisão
