# Casos de Teste — Esclarecer Configuração de Effort em 05-agentes-e-esforco.md

Status: approved
Owner: quality
Last updated: 2026-06-17

## Inputs
- User Story: 51 — Documentação Completa do pipeyml
- Task: 121 — Esclarecer configuração de Effort em 05-agentes-e-esforco.md

## CT-001 — Níveis de Effort são Configuráveis

**Tipo:** unitário
**Critério de aceitação:** "Deixa explícito que effort é opcional" e "Clareza sobre o que é configurável vs. predefinido"

**Pré-condição:**
- Arquivo `docs/pipe-yml-config/05-agentes-e-esforco.md` está disponível

**Passos:**
1. Abrir seção "Mapeamento Global de Effort"
2. Verificar se a documentação indica que o usuário **pode definir seus próprios níveis**
3. Verificar se há exemplo mostrando customização (ex: níveis diferentes dos padrões)
4. Verificar se distinção entre configuração padrão e customização está clara

**Resultado esperado:**
- Seção deixa explícito que configuração é do **usuário**, não fixa pela esteira
- Exemplo mostra que níveis podem ser nomeados/estruturados diferentemente
- Há parágrafo explicando que isso é customizável

---

## CT-002 — Modelos de IA Dependem da Disponibilidade do Usuário

**Tipo:** unitário
**Critério de aceitação:** "Modelos disponíveis dependem da IA, não da esteira"

**Pré-condição:**
- Seção "Modelos Disponíveis" está documentada

**Passos:**
1. Abrir subseção "Modelos Disponíveis"
2. Verificar se há aviso explícito que modelos listados **dependem de acesso** (API, keys, quotas)
3. Verificar se deixa claro que usuário escolhe quais modelos usar conforme disponibilidade
4. Verificar se não sugere que esteira "fornece" ou "controla" os modelos

**Resultado esperado:**
- Documentação clarifica que modelos dependem de acesso/configuração do usuário
- Não há linguagem que sugira esteira limita ou oferece modelos predefinidos
- Há menção à necessidade de credenciais/acesso para cada modelo

---

## CT-003 — Effort é Opcional

**Tipo:** unitário
**Critério de aceitação:** "Deixa explícito que effort é opcional"

**Pré-condição:**
- Seção "Atribuindo Agentes a Colunas" está documentada

**Passos:**
1. Verificar campo `effort` em exemplo de coluna
2. Verificar se documentação explica que `effort` **não é obrigatório**
3. Verificar se há parágrafo descrevendo comportamento padrão quando ausente
4. Verificar se há exemplo de coluna **sem** effort definido

**Resultado esperado:**
- Campo `effort` é marcado como opcional (ex: com comentário ou seção "optional")
- Há explicação do fallback quando não configurado
- Há exemplo de coluna funcionando sem `effort`

---

## CT-004 — Usuário Controla Agentes Disponíveis

**Tipo:** unitário
**Critério de aceitação:** "Reflete que usuário controla agentes disponíveis"

**Pré-condição:**
- Seção "Agentes Disponíveis" está documentada

**Passos:**
1. Abrir subseção "Agentes Disponíveis"
2. Verificar se lista descrita como **exemplo** ou **sugestões**, não obrigatória
3. Verificar se há parágrafo explicando que usuário pode criar **quantos agentes quiser**
4. Verificar se deixa claro que lista é referência, não predefinição

**Resultado esperado:**
- Linguagem muda de "Agentes Disponíveis" para deixar claro que são sugestões
- Há explicação que usuário cria seus próprios agentes em `.kiro/agents/`
- Não há sugestão de que estes agentes "existem por padrão" ou "devem ser usados"

---

## CT-005 — Exemplos Refletem Flexibilidade de Configuração

**Tipo:** integração
**Critério de aceitação:** "Exemplos mostram flexibilidade"

**Pré-condição:**
- Seções de exemplo estão documentadas
- Arquivo `.kiro/agents/` é mencionado

**Passos:**
1. Revisar exemplo em "Mapeamento Global de Effort"
2. Revisar exemplo em "Configuração Completa"
3. Verificar se há pelo menos um exemplo onde:
   - Níveis de effort têm nomes/estruturas diferentes dos padrões
   - Agentes são customizados ou omitidos
   - Usuário faz escolhas específicas
4. Verificar se documentação menciona como estender com agentes customizados

**Resultado esperado:**
- Exemplos mostram cenários reais de customização
- Há referência a `.kiro/agents/` para criação de agentes customizados
- Documentação deixa claro que configuração é flexível conforme necessidade

---

## CT-006 — Sem Quebra de Conteúdo Existente

**Tipo:** integração
**Critério de aceitação:** "Sem quebra de conteúdo existente"

**Pré-condição:**
- Arquivo original foi lido
- Estrutura geral é conhecida

**Passos:**
1. Verificar se seções originais estão mantidas (títulos, ordem geral)
2. Verificar se exemplos YAML ainda funcionam sintaticamente
3. Verificar se conceitos cobertos ainda existem (não foram removidos)
4. Verificar se links internos/referências ainda apontam corretamente

**Resultado esperado:**
- Estrutura geral do documento está preservada
- Exemplos YAML são válidos
- Nenhuma seção foi removida, apenas clarificada
- Documentação ainda cobre resolução de precedência, boas práticas, etc.

---

## CT-007 — Precedência Explícita na Documentação

**Tipo:** unitário
**Critério de aceitação:** "Clareza sobre o que é configurável vs. predefinido"

**Pré-condição:**
- Seção "Resolução de Precedência" está documentada

**Passos:**
1. Verificar seção "Resolução de Precedência"
2. Validar que ordem está clara: padrão agente → coluna → issue
3. Verificar se exemplo mostra comportamento com `allow-overwrite: true/false`
4. Verificar se deixa explícito qual nível pode ser customizado em cada escopo

**Resultado esperado:**
- Ordem de precedência é objetiva e não ambígua
- Exemplo de resolução é realista
- Documentação explica quando cada nível pode sobrescrever

---

## Resumo

| Caso | Descrição | Tipo |
|------|-----------|------|
| CT-001 | Configurabilidade de níveis de effort | unitário |
| CT-002 | Modelos dependem de acesso do usuário | unitário |
| CT-003 | Effort é opcional | unitário |
| CT-004 | Usuário controla agentes | unitário |
| CT-005 | Exemplos refletem flexibilidade | integração |
| CT-006 | Sem quebra de conteúdo | integração |
| CT-007 | Precedência explícita | unitário |

**Total esperado:** 7 casos de teste
**Foco:** Clarificação de conceitos (não funcionalidade), validação de linguagem e exemplos
