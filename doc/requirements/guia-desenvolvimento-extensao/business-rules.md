# Regras de Negócio — Guia de Desenvolvimento e Extensão

Status: approved
Owner: requirements
Last updated: 2026-06-16

## Inputs
- Issue #50: Guia de Desenvolvimento e Extensão (respostas do usuário em 2026-06-16T12:41:53Z)
- Contexto do projeto: esteira agentica como sistema de orquestração de agentes

## RN-001 — Escopo do Guia de Contribuição

**Descrição:** O guia de contribuição cobre apenas contribuições para o núcleo da esteira (esteira-agentica repository). Inclui bugs, melhorias, novas funcionalidades e integrações com ferramentas externas.

**Contexto:** Desenvolvedor que encontra um bug, propõe uma melhoria ou integração deseja saber o processo e padrões.

**Exceções:** Não inclui diretrizes para repositórios separados de extensões ou agentes customizados. Esses seguem padrão de esteira mas com ciclo de vida independente.

## RN-002 — Arquitetura em Alto Nível

**Descrição:** A documentação de arquitetura apresenta componentes principais e fluxo de dados em alto nível. O código é relativamente simples, justificando esta abordagem.

**Contexto:** Desenvolvedor deseja entender como o sistema funciona antes de contribuir ou estender.

**Exceções:** Detalhes de implementação e padrões de design específicos (type hints, patterns de concorrência) são documentados em comentários de código, não em guias separados.

## RN-003 — Exemplos de Agentes Personalizados

**Descrição:** O guia de criação de agentes lista exemplos de agentes mais procurados/úteis que complementam a lista existente da esteira. Exemplos incluem: Code Reviewer, Empacotador, Analista de Infra DevOps, Especialista em AWS, Azure ou outras nuvens públicas.

**Contexto:** Desenvolvedor quer criar um agente personalizado e usa exemplos como inspiração e padrão.

**Exceções:** Não inclui tutoriais de ferramentas externas (Python, GitHub API), apenas como integrar com a esteira.

## RN-004 — Suporte a APIs

**Descrição:** Por enquanto não há APIs públicas/estáveis. Ignore documentação de APIs e interfaces públicas na versão inicial. Foco em interfaces internas que extensões precisam conhecer (como criar um agente, como registrar callbacks, como acessar o board).

**Contexto:** Arquitetura ainda está em evolução e exposição de interfaces públicas será feita em versão futura.

**Exceções:** Quando APIs públicas forem definidas, criar documento separado de referência.

## RN-005 — Requisitos Não-Funcionais

**Descrição:** Não há constraints específicos para documentação técnica na versão inicial. O analista pode propor padrões de performance, versionamento e i18n quando relevante.

**Contexto:** Documentação deve ser acessível e manutenível conforme o projeto evolui.

**Exceções:** Constraints serão adicionados conforme necessidades de escala e manutenibilidade evoluirem.
