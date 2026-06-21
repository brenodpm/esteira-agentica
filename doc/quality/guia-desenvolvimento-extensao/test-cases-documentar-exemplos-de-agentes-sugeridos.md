# Casos de Teste — Documentar Exemplos de Agentes Sugeridos

Status: draft
Owner: quality
Last updated: 2026-06-21

## Inputs
- Task: #109 — Documentar Exemplos de Agentes Sugeridos
- User Story: #50 — Guia de Desenvolvimento e Extensão

## CT-001 — Arquivo de documentação existe em local correto

**Tipo:** unitário
**Critério de aceitação:** Arquivo em `doc/guias/agentes-sugeridos.md`

**Pré-condição:**
- Repositório clonado localmente

**Passos:**
1. Navegar até `doc/guias/`
2. Verificar existência de arquivo `agentes-sugeridos.md`
3. Confirmar formato é markdown (`.md`)

**Resultado esperado:**
- Arquivo existe em `doc/guias/agentes-sugeridos.md`
- Arquivo está em formato markdown

## CT-002 — Documentação lista 5 agentes sugeridos

**Tipo:** manual
**Critério de aceitação:** Documentação lista 5 agentes sugeridos

**Pré-condição:**
- Arquivo `doc/guias/agentes-sugeridos.md` existe

**Passos:**
1. Abrir arquivo de documentação
2. Identificar seção que lista agentes sugeridos
3. Contar quantidade de agentes documentados

**Resultado esperado:**
- Documento lista exatamente 5 agentes: Code Reviewer, Empacotador, Analista DevOps, Especialista AWS, Especialista Azure
- Cada agente é identificável e bem-separado no documento

## CT-003 — Cada agente contém descrição clara

**Tipo:** manual
**Critério de aceitação:** Cada agente tem descrição e responsabilidades clara

**Pré-condição:**
- Arquivo `doc/guias/agentes-sugeridos.md` existe
- Documento lista 5 agentes sugeridos

**Passos:**
1. Para cada um dos 5 agentes, verificar seção de descrição
2. Validar que descrição explica o propósito do agente
3. Verificar se responsabilidades estão claramente listadas

**Resultado esperado:**
- Cada agente possui seção de descrição (mínimo 2-3 linhas)
- Responsabilidades do agente estão explicitamente documentadas (lista ou parágrafo)
- Descrição é objetiva e evita ambiguidades

## CT-004 — Code Reviewer contém descrição e responsabilidades

**Tipo:** manual
**Critério de aceitação:** Cada agente tem descrição e responsabilidades clara

**Pré-condição:**
- Arquivo contém seção do agente "Code Reviewer"

**Passos:**
1. Localizar seção do Code Reviewer
2. Ler descrição e responsabilidades

**Resultado esperado:**
- Descrição explica que o agente faz revisão de código
- Responsabilidades incluem: análise de padrões, qualidade, validação de boas práticas

## CT-005 — Empacotador contém descrição e responsabilidades

**Tipo:** manual
**Critério de aceitação:** Cada agente tem descrição e responsabilidades clara

**Pré-condição:**
- Arquivo contém seção do agente "Empacotador"

**Passos:**
1. Localizar seção do Empacotador
2. Ler descrição e responsabilidades

**Resultado esperado:**
- Descrição explica que o agente gerencia empacotamento e build
- Responsabilidades incluem: versionamento, construção de artefatos, publicação

## CT-006 — Analista DevOps contém descrição e responsabilidades

**Tipo:** manual
**Critério de aceitação:** Cada agente tem descrição e responsabilidades clara

**Pré-condição:**
- Arquivo contém seção do agente "Analista DevOps"

**Passos:**
1. Localizar seção do Analista DevOps
2. Ler descrição e responsabilidades

**Resultado esperado:**
- Descrição explica que o agente gerencia infraestrutura e deployment
- Responsabilidades incluem: automação, monitoramento, gerenciamento de recursos

## CT-007 — Especialista AWS contém descrição e responsabilidades

**Tipo:** manual
**Critério de aceitação:** Cada agente tem descrição e responsabilidades clara

**Pré-condição:**
- Arquivo contém seção do agente "Especialista AWS"

**Passos:**
1. Localizar seção do Especialista AWS
2. Ler descrição e responsabilidades

**Resultado esperado:**
- Descrição explica que o agente especializa-se em serviços AWS
- Responsabilidades incluem: configuração AWS, otimização de custos, segurança na nuvem

## CT-008 — Especialista Azure contém descrição e responsabilidades

**Tipo:** manual
**Critério de aceitação:** Cada agente tem descrição e responsabilidades clara

**Pré-condição:**
- Arquivo contém seção do agente "Especialista Azure"

**Passos:**
1. Localizar seção do Especialista Azure
2. Ler descrição e responsabilidades

**Resultado esperado:**
- Descrição explica que o agente especializa-se em serviços Azure
- Responsabilidades incluem: configuração Azure, gerenciamento de recursos, segurança na nuvem

## CT-009 — Agentes incluem exemplos de implementação

**Tipo:** manual
**Critério de aceitação:** Exemplos de implementação (simplificados ou referências)

**Pré-condição:**
- Arquivo `doc/guias/agentes-sugeridos.md` existe

**Passos:**
1. Para cada um dos 5 agentes, procurar por seção de "Exemplo" ou "Implementação"
2. Verificar se há código simplificado ou referência ao template

**Resultado esperado:**
- Cada agente possui exemplo de implementação (código ou referência)
- Exemplos são simplificados e servem como ponto de partida
- Exemplos referenciam `doc/guias/criar-agente-personalizado.md` quando apropriado

## CT-010 — Documentação explica como registrar novo agente

**Tipo:** manual
**Critério de aceitação:** Mostra como registrar novo agente na esteira

**Pré-condição:**
- Arquivo `doc/guias/agentes-sugeridos.md` existe

**Passos:**
1. Procurar por seção sobre "Como Registrar" ou "Registrando Agentes"
2. Validar que processo de registro está documentado

**Resultado esperado:**
- Seção descreve passos para registrar novo agente na esteira
- Instruções referem-se a arquivo de configuração ou processo específico
- Conteúdo liga com o guia de criar agente personalizado

## CT-011 — Referência ao guia de criar agente personalizado

**Tipo:** manual
**Critério de aceitação:** Referencia guia de criar agente (CA-002)

**Pré-condição:**
- Arquivo `doc/guias/agentes-sugeridos.md` existe
- Arquivo `doc/guias/criar-agente-personalizado.md` existe

**Passos:**
1. Procurar por referências a "criar-agente-personalizado" ou links internos
2. Validar que link está presente e é navegável

**Resultado esperado:**
- Documento referencia `doc/guias/criar-agente-personalizado.md`
- Referência aparece em contexto apropriado (ex: seção de extensão ou exemplos)
- Link usa sintaxe markdown correta

## CT-012 — Estrutura e formatação do documento

**Tipo:** manual
**Critério de aceitação:** Documentação lista 5 agentes sugeridos

**Pré-condição:**
- Arquivo `doc/guias/agentes-sugeridos.md` existe

**Passos:**
1. Verificar estrutura geral do documento (headers, seções)
2. Validar consistência de formatação entre agentes
3. Confirmar que índice/sumário está presente (se aplicável)

**Resultado esperado:**
- Documento segue padrão markdown com headers bem-estruturados
- Formatação é consistente entre todas as seções de agentes
- Documento é fácil de navegar e ler
