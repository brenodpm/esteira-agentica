# Casos de Teste — Documentar Como Criar Agente Personalizado

Status: draft
Owner: quality
Last updated: 2026-06-19

## Inputs
- Task: #108 — Documentar Como Criar Agente Personalizado
- User Story: #50 — Guia de Desenvolvimento e Extensão

## CT-001 — Arquivo de documentação existe em local correto

**Tipo:** unitário
**Critério de aceitação:** Arquivo em `doc/guias/criar-agente-personalizado.md`

**Pré-condição:**
- Repositório clonado localmente

**Passos:**
1. Navegar até `doc/guias/`
2. Verificar existência de arquivo `criar-agente-personalizado.md`
3. Confirmar formato é markdown (`.md`)

**Resultado esperado:**
- Arquivo existe em `doc/guias/criar-agente-personalizado.md`
- Arquivo está em formato markdown

## CT-002 — Documentação contém seção "Como Criar um Agente"

**Tipo:** manual
**Critério de aceitação:** Documentação contém seção "Como Criar um Agente"

**Pré-condição:**
- Arquivo `doc/guias/criar-agente-personalizado.md` existe

**Passos:**
1. Abrir arquivo de documentação
2. Procurar por seção com título contendo "Como Criar" ou "Creating an Agent" (ou equivalente em português)
3. Validar que a seção descreve passo-a-passo para criar agente

**Resultado esperado:**
- Seção "Como Criar um Agente" existe e é bem-delimitada
- Seção está facilmente localizável (via índice ou título)
- Conteúdo descreve processo de início ao fim

## CT-003 — Template de código reutilizável presente

**Tipo:** manual
**Critério de aceitação:** Inclui template de código reutilizável

**Pré-condição:**
- Documentação contém seção "Como Criar um Agente"

**Passos:**
1. Localizar template de código na documentação
2. Verificar se template inclui:
   - Estrutura básica de classe/arquivo de agente
   - Callbacks registrados
   - Integração ao sistema
3. Confirmar código é exibido em bloco de código markdown

**Resultado esperado:**
- Template de código está presente
- Estrutura é clara e bem-formatada
- Template inclui elementos essenciais de um agente (callbacks, integração)

## CT-004 — Template pode ser copiado e adaptado com edições mínimas

**Tipo:** integração
**Critério de aceitação:** Template pode ser copiado e adaptado com edições mínimas

**Pré-condição:**
- Template de código existe e é funcional

**Passos:**
1. Copiar template exato da documentação
2. Identificar pontos de personalização (placeholders, variáveis)
3. Contar número de mudanças necessárias para um caso simples
4. Validar que não requer reformulação estrutural

**Resultado esperado:**
- Pontos de personalização são claros (ex: `<SEU_NOME>`, `def nome_agente():`)
- Máximo 5 mudanças necessárias para caso simples
- Template é reutilizável sem reformulação estrutural

## CT-005 — Exemplo pronto funciona end-to-end

**Tipo:** integração
**Critério de aceitação:** Exemplo pronto funciona end-to-end

**Pré-condição:**
- Documentação contém exemplo funcionável

**Passos:**
1. Copiar exemplo da documentação (nome, código, setup)
2. Seguir passos documentados para integração
3. Executar agente em ambiente local
4. Validar que agente executa sem erros

**Resultado esperado:**
- Exemplo não possui erros de sintaxe
- Agente pode ser importado e executado
- Fluxo completo (input → execução → output) funciona
- Não requer dependências externas não-documentadas

## CT-006 — Exemplos contêm menos de 100 linhas

**Tipo:** unitário
**Critério de aceitação:** Exemplos < 100 linhas

**Pré-condição:**
- Arquivo de documentação completo

**Passos:**
1. Localizar todos os exemplos de código no documento
2. Contar linhas de código de cada exemplo
3. Validar que nenhum exemplo excede 100 linhas

**Resultado esperado:**
- Template principal < 100 linhas
- Cada exemplo adicional < 100 linhas
- Documentação é concisa e fácil de seguir

## CT-007 — Passo-a-passo: definir → criar → registrar → integrar → testar

**Tipo:** manual
**Critério de aceitação:** Passo-a-passo: definir responsabilidades → criar classe → registrar callbacks → integrar ao orchestrator

**Pré-condição:**
- Documentação contém seção "Como Criar um Agente"

**Passos:**
1. Localizar seção de passo-a-passo
2. Verificar presença dos seguintes passos em ordem lógica:
   - **Definir**: responsabilidades e escopo do agente
   - **Criar**: classe/arquivo do agente
   - **Registrar**: callbacks necessários
   - **Integrar**: ao orchestrator/sistema
   - **Testar**: localmente antes de integração na esteira
3. Validar cada passo está descrito com clareza

**Resultado esperado:**
- Todos os 5 passos estão presentes e bem-documentados
- Sequência é lógica e fácil de seguir
- Cada passo explica o "porquê" além do "como"

## CT-008 — Documentação referencia pontos de extensão da arquitetura

**Critério de aceitação:** Referencia pontos de extensão documentados em CA-001 (arquitetura)

**Tipo:** manual

**Pré-condição:**
- Arquivo `doc/architecture-overview.md` contém "Pontos de Extensão"
- Documentação de agente está completa

**Passos:**
1. Localizar seção de pontos de extensão em `doc/architecture-overview.md`
2. Verificar que documentação de criação de agente referencia:
   - Localização física onde registrar novo agente (`.kiro/agents/`)
   - Quando usar cada ponto de extensão
   - Link ou referência ao documento de arquitetura
3. Validar alinhamento entre documentos

**Resultado esperado:**
- Documentação referencia explicitamente pontos de extensão de arquitetura
- Conexão entre agente novo e sistema geral é clara
- Desenvolvedor sabe onde registrar e como integrar

## CT-009 — Documento contém exemplo prático completo (< 100 linhas)

**Tipo:** integração
**Critério de aceitação:** Exemplo pronto end-to-end (criar agente simples, rodar, testar)

**Pré-condição:**
- Documentação contém todos os passos anteriores

**Passos:**
1. Localizar exemplo prático completo
2. Validar que exemplo inclui:
   - Definição de responsabilidade
   - Código de classe/arquivo
   - Registro de callback
   - Integração ao sistema
   - Como testar (comando ou procedimento)
3. Contar linhas do exemplo
4. Tentar executar exemplo conforme documentado

**Resultado esperado:**
- Exemplo prático está presente e bem-delimitado
- Exemplo < 100 linhas
- Desenvolvedor consegue seguir do início ao fim
- Exemplo é funcional e testável

## CT-010 — Documentação aborda como testar agente antes de integrar

**Tipo:** manual
**Critério de aceitação:** Documentar como testar agente antes de integrar na esteira

**Pré-condição:**
- Documentação contém seção "Como Criar um Agente"

**Passos:**
1. Localizar seção sobre testes/validação
2. Verificar documentação inclui:
   - Como executar agente localmente
   - Como validar saída
   - Como debugar problemas
   - Quando agente está pronto para integração
3. Validar que instruções são claras e executáveis

**Resultado esperado:**
- Seção de testes está presente
- Instruções são específicas e testáveis
- Desenvolvedor sabe como validar seu agente funciona
- Critério de sucesso é claro

## CT-011 — Escopo: apenas templates, sem implementações específicas

**Tipo:** manual
**Critério de aceitação:** Escopo: apenas templates; fora: implementação de agentes específicos (devops, cloud, etc)

**Pré-condição:**
- Documentação está completa

**Passos:**
1. Verificar ausência de implementações específicas de domínio:
   - DevOps agent
   - Cloud agent
   - Security agent
2. Confirmar documentação mantém foco em template reutilizável
3. Validar não há tutoriais de LLM ou ChatGPT

**Resultado esperado:**
- Documentação contém apenas template genérico
- Sem implementações específicas de agentes
- Sem guias de ferramentas externas (LLM, ChatGPT)
- Foco é em padrão/padrões reutilizáveis

## CT-012 — Documento é compreensível para novo desenvolvedor

**Tipo:** manual
**Critério de aceitação:** Deve ser compreensível para desenvolvedor que quer implementar agente personalizado

**Pré-condição:**
- Documentação está completa

**Passos:**
1. Revisar estrutura geral (índice, títulos)
2. Validar linguagem é clara (não-jargão técnico excessivo)
3. Verificar presença de exemplos e contexto
4. Confirmar não assume conhecimento específico não-documentado

**Resultado esperado:**
- Estrutura é clara e navegável
- Linguagem é acessível
- Novo desenvolvedor consegue seguir sem conhecimento prévio do sistema
- Documentação antecipa dúvidas comuns
