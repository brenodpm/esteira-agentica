# ADR-004 — Suporte a Docker como alternativa, não primário

Status: accepted
Owner: architecture
Last updated: 2026-06-22

## Inputs
- Regra de negócio RN-004: Ambientes suportados local e Docker
- Non-functional requirement: Independência de plataforma
- Análise da base de código atual (Python puro, sem containerização)

## Contexto

Definir se Docker será abordagem primária (recomendada) ou alternativa (para casos específicos) na instalação.

## Decisão

Docker será abordagem alternativa. Instalação local será método primário e recomendado.

## Justificativa

- **Simplicidade primeira:** usuários podem começar sem conhecimento de Docker
- **Menos dependências:** não requer Docker instalado (um pré-requisito a menos)
- **Debug mais fácil:** problemas em ambiente local são mais fáceis de diagnosticar
- **Compatível com base atual:** projeto já funciona bem em instalação local
- **Flexibilidade:** Docker como escape para ambientes problemáticos

## Consequências

- **Positivas:**
  - Menor barreira de entrada para iniciantes
  - Instalação mais rápida na maioria dos casos
  - Melhor experiência de debugging
  
- **Negativas:**
  - Possíveis problemas de dependências em ambientes exóticos
  - Docker pode ser necessário para alguns usuários (corporate environments)
  
- **Riscos:**
  - Ambientes com Python conflitante podem ter dificuldades
  - **Mitigação:** seção Docker bem documentada como alternativa + troubleshooting para problemas de ambiente
