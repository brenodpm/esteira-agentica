# Criar Index Generator (orquestrador)

effort: low

## User Story
49-pagina_inicial_de_documentacao

## Descrição
Implementar script que orquestra os 4 componentes (Content Aggregator, Navigation Builder, Template Renderer) em sequência para gerar página inicial completa de forma automática.

## Escopo técnico
- Ler configuração (paths, personas, limites)
- Chamar Content Aggregator
- Validar saída (falhar se metadados faltam)
- Chamar Navigation Builder
- Validar navegação (falhar se > 3 cliques)
- Chamar Template Renderer
- Salvar `/docs/index.html` final
- Logging de etapas e erros
- Testes de fluxo completo end-to-end

## Fora de escopo
- Publicação em GitHub Pages
- Sincronização de versões
- Rollback automático

## Critério de aceite
- Index Generator executa fluxo completo sem erros
- Valida output de cada etapa
- Falha gracefully com mensagens claras se validação falhar
- Logs informativos para debug
- Teste end-to-end: estrutura `/docs` → `/docs/index.html`
- Arquivo final válido e navegável

/blocked_by 52-content-aggregator 53-navigation-builder 55-template-renderer
/branch epic/49-pagina_inicial_de_documentacao
