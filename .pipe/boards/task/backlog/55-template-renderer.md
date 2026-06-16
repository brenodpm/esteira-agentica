# Implementar Template Renderer

effort: medium

## User Story
49-pagina_inicial_de_documentacao

## Descrição
Implementar script que recebe estrutura de navegação do Navigation Builder e renderiza página HTML final usando template criado na task 54. Injeta dados dinâmicos (seções, links, casos de uso) no HTML.

## Escopo técnico
- Ler estrutura de navegação em JSON
- Render template HTML com Jinja2 ou similar
- Injetar dados por persona (seções, links, atalhos)
- Gerar arquivo `/docs/index.html` final
- Incluir testes de rendering: múltiplas personas, valores nulos, caracteres especiais
- Validar HTML gerado (W3C)
- Garantir performance (geração < 100ms)

## Fora de escopo
- Minificação de assets
- Cache busting
- Deploy automático

## Critério de aceite
- Renderer lê estrutura de navegação corretamente
- HTML gerado é válido e bem-formado
- Todos os dados injetados aparecem no HTML
- Testes cobrem: dados válidos, valores vazios, caracteres especiais
- Arquivo final < 100KB
- Geração completada em < 100ms

/blocked_by 53-navigation-builder 54-template-html
/branch epic/49-pagina_inicial_de_documentacao
