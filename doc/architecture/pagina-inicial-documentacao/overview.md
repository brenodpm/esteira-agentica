# Architecture Overview — Página Inicial de Documentação

Status: approved
Owner: architecture
Last updated: 2024-06-14

## Inputs
- `.pipe/boards/story/arquitetura/49-pagina_inicial_de_documentacao.md`
- Estrutura existente em `/docs`

## Visão geral
Sistema de navegação centralizada para documentação do projeto, organizando conteúdo por perfil de usuário (iniciante, avançado, desenvolvedor) e fornecendo acesso rápido a casos de uso comuns.

## Estilo arquitetural
**Static Site Generator (SSG)** - Estrutura baseada em arquivos Markdown organizados hierarquicamente, processados para gerar uma página inicial estática. Justificativa: simplicidade de manutenção, versionamento junto com código, sem dependências de runtime.

## Componentes
| Componente | Responsabilidade |
|-----------|------------------|
| Index Generator | Processa estrutura de arquivos e gera página inicial |
| Content Aggregator | Coleta metadados de seções de documentação |
| Navigation Builder | Constrói estrutura de navegação por perfil |
| Template Renderer | Aplica templates para apresentação final |

## Fluxo principal
1. Content Aggregator varre estrutura `/docs` e extrai metadados
2. Navigation Builder organiza conteúdo por perfis de usuário
3. Index Generator cria estrutura de navegação hierárquica
4. Template Renderer gera página inicial final
