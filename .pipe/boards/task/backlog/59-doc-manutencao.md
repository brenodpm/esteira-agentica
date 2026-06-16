# Documentar guia de uso e extensão da página inicial

effort: low

## User Story
49-pagina_inicial_de_documentacao

## Descrição
Criar documentação clara sobre como adicionar novas seções, atualizar metadados e manter a página inicial de documentação. Inclui guia de convenções, troubleshooting e exemplos.

## Escopo técnico
- Criar `/docs/MANUTENCAO.md` com:
  - Como adicionar nova seção (passo-a-passo)
  - Convenções de metadados (frontmatter YAML)
  - Como executar Index Generator localmente
  - Troubleshooting: metadados faltando, links quebrados
  - Exemplos de README.md para cada persona
- Atualizar `/docs/ESTRUTURA.md` com fluxo completo
- Documentar em `README.md` root com link para docs

## Fora de escopo
- Criação de conteúdo de documentação do projeto
- Suporte contínuo em issues

## Critério de aceite
- Guia cobre: adicionar seção, metadados, rodar generator, troubleshoot
- Exemplos estão presentes e funcionais
- Sem jargão técnico desnecessário
- Referencia ADRs quando relevante

/blocked_by 56-index-generator
/branch epic/49-pagina_inicial_de_documentacao
