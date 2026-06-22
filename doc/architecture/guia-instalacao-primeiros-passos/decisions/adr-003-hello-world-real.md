# ADR-003 — Hello-world com exemplo real vs simulado

Status: accepted
Owner: architecture
Last updated: 2026-06-22

## Inputs
- Regra de negócio RN-002: Hello-world executável
- Regra de negócio RN-008: Gitflow simplificado
- Non-functional requirement: Sem segredos em exemplo

## Contexto

O hello-world pode usar dados reais (criar issue real no projeto) ou dados simulados (mock/exemplo local). Precisamos decidir qual abordagem usar.

## Decisão

Hello-world usará exemplo real mas controlado: criar issue em board de teste com automação mínima.

## Justificativa

- **Experiência autêntica:** usuário vê resultado real da esteira funcionando
- **Validação completa:** testa integração GitHub + esteira local + agentes
- **Confiança imediata:** sucesso no hello-world gera confiança no sistema
- **Debugging efetivo:** problemas reais aparecem e podem ser diagnosticados
- **Atende RN-002:** exemplo funcional sem simulação

## Consequências

- **Positivas:**
  - Demonstração convincente das capacidades do sistema
  - Usuário termina com repositório funcional em suas mãos
  - Facilita transição para casos de uso reais
  
- **Negativas:**
  - Requer configuração de credentials (GitHub token)
  - Pode falhar por problemas de rede/API
  - Deixa "lixo" no repositório (issues de teste)
  
- **Riscos:**
  - Rate limiting do GitHub pode bloquear execução
  - Falhas de conectividade podem frustrar usuário
  - **Mitigação:** incluir troubleshooting para problemas comuns de API
