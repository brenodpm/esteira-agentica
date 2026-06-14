# Regras de Negócio — Página Inicial de Documentação

Status: approved
Owner: requirements
Last updated: 2026-06-14

## Inputs
- `.pipe/boards/story/arquitetura/49-pagina_inicial_de_documentacao.md`
- Epic: 48-criacao_da_documentacao_do_projeto

## RN-001 — Índice Centralizado

**Descrição:** A página inicial deve funcionar como ponto único de entrada para toda a documentação do projeto, evitando fragmentação.

**Contexto:** Novos usuários ou qualquer pessoa buscando documentação pela primeira vez.

**Exceções:** Nenhuma — sempre deve servir como índice centralizado.

## RN-002 — Segmentação por Persona

**Descrição:** O conteúdo deve ser organizado e apresentado diferentemente para três personas: iniciante, usuário experiente e desenvolvedor.

**Contexto:** Cada persona tem necessidades e profundidade de conteúdo distintas.

**Exceções:** Conteúdo transversal (glossário, FAQ) pode aparecer em todas as personas.

## RN-003 — Limite de Navegação (Regra dos 3 Cliques)

**Descrição:** Qualquer usuário deve localizar a documentação relevante em no máximo 3 cliques a partir da página inicial.

**Contexto:** Usabilidade crítica — usuários abandam se a navegação é profunda.

**Exceções:** Nenhuma — requisito testável e não negociável.

## RN-004 — Não-Duplicação de Conteúdo

**Descrição:** A página inicial deve agregar links para conteúdo, nunca duplicá-lo.

**Contexto:** Manutenção — duplicação causaria inconsistências e esforço manual.

**Exceções:** Resumos/snippets de até 2 linhas para contexto rápido são permitidos.

## RN-005 — Atalhos para Casos de Uso Comuns

**Descrição:** Deve haver links/botões diretos para os 5-7 casos de uso mais frequentes (instalação, configuração básica, criação de story, troubleshooting).

**Contexto:** Reduz tempo de busca para fluxos críticos.

**Exceções:** Pode variar por versão/release se novos casos de uso emergirem.

## RN-006 — Extensibilidade

**Descrição:** A estrutura deve permitir adição de novas seções sem refactoring da página inicial.

**Contexto:** Projeto em evolução — documentação crescerá.

**Exceções:** Nenhuma — deve suportar crescimento até 50 seções.
