# Casos de Teste — Aprofundar explicações em 03-gitflows.md

Status: approved
Owner: quality
Last updated: 2026-06-19

## Inputs
- [US 51 — Documentação Completa do pipeyml](.pipe/boards/story/aguardando-tasks/51-documentacao_completa_do_pipe_yml.md)
- [Tarefa 119 — Aprofundar explicações em 03-gitflows.md](.pipe/boards/task/execucao-testes/119-aprofundar_explicacoes_em_03_gitflows_md.md)

## CT-001 — Explicações sobre criação de flows personalizados

**Tipo:** manual
**Critério de aceitação:** "Dado que quero ajustar gitflows, quando leio sobre configuração de flow, então entendo como criar flows personalizados"

**Pré-condição:**
- Arquivo docs/pipe-yml-config/03-gitflows.md existe e foi expandido
- Usuário com conhecimento básico de gitflows

**Passos:**
1. Abrir arquivo docs/pipe-yml-config/03-gitflows.md
2. Localizar seção "Criando Gitflows Personalizados"
3. Verificar se há seção dedicada com exemplos de flows customizados
4. Validar se os exemplos cobrem casos de uso comuns (docs, staging, qa, refactor, security, performance)
5. Verificar clareza das explicações sobre estrutura mínima e validações

**Resultado esperado:**
- Seção "Criando Gitflows Personalizados" existe com:
  - Estrutura mínima clara
  - Mínimo 4 casos de uso diferentes documentados
  - Validações explicadas (prefix único, referências válidas, etc.)
  - Exemplos práticos com outputs esperados

## CT-002 — Contexto sobre resolução de prefixos dinâmicos

**Tipo:** manual
**Critério de aceitação:** "Dado que quero ajustar gitflows, quando leio sobre configuração de flow, então entendo como criar flows personalizados"

**Pré-condição:**
- Arquivo docs/pipe-yml-config/03-gitflows.md foi atualizado
- Conceitos de branch fixa vs prefixo dinâmico são básicos

**Passos:**
1. Abrir arquivo docs/pipe-yml-config/03-gitflows.md
2. Localizar seção "Resolvendo Prefixos Dinâmicos"
3. Verificar se o processo de resolução está detalhado com passos numerados
4. Validar casos de uso comuns (Epic → Release, Feature → Epic)
5. Verificar se cenários de erro estão documentados

**Resultado esperado:**
- Seção "Resolvendo Prefixos Dinâmicos" contém:
  - Processo claro com mínimo 3 passos
  - Exemplos de resolução com label `/branch` e comentários HTML
  - Mínimo 2 casos de uso comuns com fluxo esperado
  - Cenários de erro documentados

## CT-003 — Exemplos contextualizados e casos de uso

**Tipo:** manual
**Critério de aceitação:** "Dado que preciso configurar boards personalizados, quando consulto a documentação, então encontro exemplos para meu caso de uso"

**Pré-condição:**
- Arquivo expandido com novos exemplos
- Usuário busca by-pass rápido para seus cenários

**Passos:**
1. Abrir arquivo docs/pipe-yml-config/03-gitflows.md
2. Verificar seção "Estratégias de Branching"
3. Validar se há exemplos para GitFlow tradicional, GitHub Flow e Epic-Based Flow
4. Verificar se cada exemplo mostra configuração YAML completa com outputs
5. Validar clareza e contexto de cada estratégia

**Resultado esperado:**
- Seção "Estratégias de Branching" com:
  - Mínimo 3 estratégias documentadas (GitFlow, GitHub Flow, Epic-Based)
  - Cada estratégia com configuração YAML clara
  - Contexto explicando quando usar cada uma
  - Exemplo prático de fluxo resultante

## CT-004 — Impacto e comportamento das configurações

**Tipo:** manual
**Critério de aceitação:** "Dado que encontro erro de configuração, quando verifico a documentação, então identifico o problema rapidamente"

**Pré-condição:**
- Seção de impacto de configurações foi expandida
- Usuário enfrenta decisões sobre cleanup, create/merge

**Passos:**
1. Abrir arquivo docs/pipe-yml-config/03-gitflows.md
2. Localizar seção "Impacto das Configurações"
3. Verificar subseções:
   - `cleanup: true` vs `cleanup: false`
   - Impacto de `prefix`
   - Impacto de `create` e `merge`
   - Comportamentos avançados
4. Validar se explicações cobrem consequências práticas
5. Verificar seção "Resolução de Problemas Comuns"

**Resultado esperado:**
- Seção "Impacto das Configurações" contém:
  - Explicação clara do que `cleanup` controla (local vs remote)
  - Impacto de cada parâmetro no fluxo de trabalho
  - Comportamentos avançados como referência cruzada
  - Seção "Resolução de Problemas Comuns" com mínimo 3 problemas + soluções
