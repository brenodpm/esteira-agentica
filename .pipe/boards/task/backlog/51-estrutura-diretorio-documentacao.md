# Estruturar diretório base de documentação com seções por persona

effort: low

## User Story
49-pagina_inicial_de_documentacao

## Descrição
Criar estrutura de diretórios em `/docs` com subdireções para cada persona (iniciante, avançado, desenvolvedor) e criar arquivos `README.md` em cada seção com metadados de identificação.

## Escopo técnico
- Criar diretórios: `/docs/iniciante`, `/docs/avancado`, `/docs/desenvolvedor`
- Criar `README.md` em cada diretório com frontmatter (título, descrição, persona)
- Criar `/docs/shared` para conteúdo transversal (glossário, FAQ)
- Documentar convenção de metadados em `/docs/ESTRUTURA.md`

## Fora de escopo
- Migração de conteúdo existente
- Criação de páginas iniciais ou templates
- Automação de build

## Critério de aceite
- Estrutura de diretórios criada e versionada
- Cada seção tem `README.md` com metadados
- Convenções documentadas
- Sem erros de permissão ou encoding

/branch epic/49-pagina_inicial_de_documentacao
