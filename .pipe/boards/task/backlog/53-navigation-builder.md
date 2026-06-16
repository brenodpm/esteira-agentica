# Implementar Navigation Builder

effort: medium

## User Story
49-pagina_inicial_de_documentacao

## Descrição
Implementar script que recebe JSON do Content Aggregator e constrói estrutura de navegação segmentada por persona. Gera mapa de: persona → seções → links com profundidade máxima.

## Escopo técnico
- Receber JSON do Content Aggregator
- Organizar conteúdo por persona (iniciante, avançado, desenvolvedor)
- Validar limite de 3 cliques (profundidade máxima de navegação)
- Identificar 5-7 casos de uso comuns por persona
- Gerar estrutura de navegação hierárquica
- Incluir testes de profundidade e cobertura de personas
- Validar nenhuma seção fica órfã (sem acesso)

## Fora de escopo
- Renderização de componentes
- Validação de links (responsabilidade de CI/CD)
- Internacionalização

## Critério de aceite
- Navigation Builder lê JSON do Content Aggregator
- Mapeia seções para cada persona corretamente
- Todos os acessos respeitam limite de 3 cliques
- Casos de uso comuns identificados por persona
- Testes cobrem: múltiplas personas, limite de cliques, conteúdo transversal
- Estrutura serializa para JSON válido

/blocked_by 52-content-aggregator
/branch epic/49-pagina_inicial_de_documentacao
