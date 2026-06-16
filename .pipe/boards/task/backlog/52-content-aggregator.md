# Implementar Content Aggregator

effort: medium

## User Story
49-pagina_inicial_de_documentacao

## Descrição
Implementar script Python que varre estrutura `/docs` e extrai metadados de cada seção (titulo, descrição, persona, casos de uso). Retorna JSON estruturado para consumo por Index Generator.

## Escopo técnico
- Ler arquivos `README.md` em `/docs` recursivamente
- Extrair frontmatter YAML (titulo, descricao, persona, casos_uso)
- Validar estrutura e metadados obrigatórios
- Retornar JSON com índice hierárquico
- Incluir testes unitários para parsing de metadados
- Tratar erros de arquivo malformado gracefully

## Fora de escopo
- Geração de página HTML/CSS
- Integração com GitHub Pages
- Deploy automático

## Critério de aceite
- Script lê estrutura `/docs` corretamente
- Extrai metadados de todos os README.md
- Valida presença de campos obrigatórios (titulo, persona)
- Retorna JSON bem-formado
- Testes cobrem casos: arquivo válido, metadados faltantes, diretório vazio
- Sem exceções não tratadas

/blocked_by 51-estrutura-diretorio-documentacao
/branch epic/49-pagina_inicial_de_documentacao
