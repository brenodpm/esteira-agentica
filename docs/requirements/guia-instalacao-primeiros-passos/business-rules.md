# Regras de Negócio — Guia de Instalação e Primeiros Passos

Status: approved
Owner: requirements
Last updated: 2026-06-19

## Inputs
- Issue #52: Guia de Instalação e Primeiros Passos (story requisitos)
- pipe.yml: configurações globais do projeto
- README.md: documentação existente
- src/__main__.py: ponto de entrada do projeto

## RN-001 — Instalação executável em 15 minutos

**Descrição:** Um desenvolvedor novo deve conseguir instalar e executar a esteira com sucesso em no máximo 15 minutos, seguindo apenas o guia.

**Contexto:** Primeira experiência do usuário com o projeto. Inclui: clone, instalação de dependências, execução básica.

**Exceções:** Não inclui configurações avançadas, integração com CI/CD ou personalização de agentes.

## RN-002 — Hello-world executável

**Descrição:** Após seguir o guia, o desenvolvedor deve conseguir criar uma primeira automação simples que funcione sem erros.

**Contexto:** Exemplo funcional que demonstra como agentes, boards e flows funcionam na prática.

**Exceções:** Não inclui automações complexas com múltiplos agentes ou integrações externas.

## RN-003 — Conceitos explicados antes dos passos técnicos

**Descrição:** Antes de qualquer instrução técnica, o guia deve explicar os 4 conceitos-chave:
- Agentes: o que são, como preenchê-los (JSON), atributos obrigatórios vs opcionais, onde buscar informações
- Boards: conceitos básicos necessários para funcioná-lo
- pipe.yml: configuração central e como não modificá-lo sem entender impacto
- model/effort: configurações básicas do projeto

**Contexto:** Reduz confusão e suposições durante a instalação.

**Exceções:** Não inclui conceitos avançados como custom model routing, rate limiting ou otimização de prompts.

## RN-004 — Ambientes suportados

**Descrição:** O guia deve cobrir instalação em:
- Local (máquina do desenvolvedor)
- Docker (containerizado)

**Contexto:** Flexibilidade de setup conforme ambiente do desenvolvedor.

**Exceções:** CI/CD será abordado em demanda não-bloqueante futura.

## RN-005 — Pré-requisitos claros

**Descrição:** O guia deve listar e explicar versões de: Python, Git, Docker (se aplicável) que o projeto utiliza.

**Contexto:** Evita erros de compatibilidade e suposições sobre ambientes.

**Exceções:** Nenhuma.

## RN-006 — Troubleshooting integrado

**Descrição:** Seção "Encontrei erro durante instalação" que mapeia erros comuns e suas soluções.

**Contexto:** Reduz fricção para usuários que encontram problemas.

**Exceções:** Nenhuma.

## RN-007 — Um único arquivo de documentação

**Descrição:** Todo o conteúdo será em um arquivo único (não múltiplos).

**Contexto:** Simplicidade de descoberta e manutenção.

**Exceções:** Nenhuma.

## RN-008 — Gitflow simplificado

**Descrição:** O hello-world deve usar apenas as operações essenciais: clone, checkout de branch, commit, push — sem operações CI/CD ou deployment.

**Contexto:** Exemplo mínimo viável que demonstra workflow sem complexidade.

**Exceções:** CI/CD integrado será abordado em demanda futura.
