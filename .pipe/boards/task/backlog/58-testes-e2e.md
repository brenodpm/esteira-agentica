# Testar página inicial end-to-end: navegação, acessibilidade, performance

effort: medium

## User Story
49-pagina_inicial_de_documentacao

## Descrição
Implementar suite de testes que valida página inicial completa: navegação em 3 cliques, acessibilidade WCAG AA, performance < 2s primeira carga, responsividade múltiplos dispositivos.

## Escopo técnico
- Testes de navegação: todos acessos em máximo 3 cliques
- Testes de acessibilidade: contraste, ARIA, navegação por teclado
- Testes de performance: métricas LCP, CLS, FID
- Testes de responsividade: 320px, 768px, 1024px, 2560px
- Testes de dados: todas personas têm seções, casos de uso listados
- Testes de validação: HTML válido, links internos válidos
- Automação: executa em CI/CD antes de deploy
- Tools: pytest, axe-core, lighthouse

## Fora de escopo
- Testes de browser cross-browser (apenas Chrome headless)
- Testes de performance contra usuários reais (RUM)
- A/B testing

## Critério de aceite
- Testes cobrem: navegação 3-cliques, acessibilidade, performance, responsividade
- Todos os testes passam
- Coverage > 90% de caminhos de navegação
- Performance < 2s em simulação de rede 4G
- Testes rodam em CI/CD
- Relório de coverage gerado

/blocked_by 56-index-generator
/branch epic/49-pagina_inicial_de_documentacao
