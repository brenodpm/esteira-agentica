# Casos de Teste — Aprofundar explicações em 04-boards-e-colunas.md

Status: draft
Owner: quality
Last updated: 2026-06-17

## Inputs
- User Story: 51 — Documentação Completa do pipeyml
- Task: 120 — Aprofundar explicações em 04-boards-e-colunas.md

## CT-001 — Explicações expandidas: Conceito de Boards

**Tipo:** manual
**Critério de aceitação:** Explicações expandidas com maior detalhe

**Pré-condição:**
- Arquivo `docs/pipe-yml-config/04-boards-e-colunas.md` foi revisado
- Seção "Estrutura Base" ou similar contém definição de boards

**Passos:**
1. Abrir arquivo `docs/pipe-yml-config/04-boards-e-colunas.md`
2. Localizar explicação sobre o conceito de "boards"
3. Verificar se a explicação contém:
   - O que é um board
   - Relação com GitHub Projects V2
   - Função organizacional dentro da esteira
   - Sincronização com repositório

**Resultado esperado:**
- Explicação de boards contém pelo menos 3-4 sentences com contexto adicional
- Deixa claro por que boards existem e qual problema resolvem
- Diferencia boards de colunas
- Menciona ciclo de vida de um board

---

## CT-002 — Explicações expandidas: Conceito de Colunas

**Tipo:** manual
**Critério de aceitação:** Explicações expandidas com maior detalhe

**Pré-condição:**
- Arquivo `docs/pipe-yml-config/04-boards-e-colunas.md` foi revisado
- Seção sobre colunas existe no documento

**Passos:**
1. Abrir arquivo `docs/pipe-yml-config/04-boards-e-colunas.md`
2. Localizar explicação sobre colunas
3. Verificar se a explicação contém:
   - O que é uma coluna
   - Como uma coluna se relaciona com um board
   - Estados que uma issue atravessa em colunas
   - Responsabilidade de cada coluna

**Resultado esperado:**
- Explicação de colunas tem detalhe suficiente para iniciante entender fluxo
- Descreve transição de issue entre colunas
- Menciona agentes e ações associadas
- Diferencia colunas manuais vs automatizadas

---

## CT-003 — Contexto claro: Configuração de Transições (change)

**Tipo:** manual
**Critério de aceitação:** Contexto claro sobre cada configuração

**Pré-condição:**
- Seção de configuração de transições (change) existe
- Exemplo de transições está documentado

**Passos:**
1. Abrir `docs/pipe-yml-config/04-boards-e-colunas.md`
2. Localizar seção sobre "change" ou transições
3. Verificar se cada tipo de transição contém:
   - `advance`: quando é executado, fluxo normal
   - `reprovar`: cenário de rejeição, volta para onde
   - `cancelar`: quando e por quê
   - `falha`: quando testes falham
   - `bloquear`: bloqueio por dependência
4. Validar que há explicação do comportamento esperado para cada

**Resultado esperado:**
- Cada chave de transição tem descrição de quando é acionada
- Diferença entre transições é clara (não confunde `reprovar` com `falha`)
- Exemplo prático mostra fluxo de uma issue passando por transições
- Deixa claro que transições são eventos, não ações

---

## CT-004 — Contexto claro: Configuração de gitevents

**Tipo:** manual
**Critério de aceitação:** Contexto claro sobre cada configuração

**Pré-condição:**
- Seção sobre "gitevents" existe ou está descrita
- Tipos de eventos git estão listados

**Passos:**
1. Abrir `docs/pipe-yml-config/04-boards-e-colunas.md`
2. Localizar explicação sobre gitevents
3. Verificar se contém contexto sobre:
   - `create`: quando cria branch, qual tipo de branch
   - `keep`: mantém branch existente, por quê
   - `merge`: quando solicita merge, qual workflow
4. Validar que há explicação de quando usar cada um

**Resultado esperado:**
- Deixa claro que gitevents são eventos que acontecem quando issue chega/sai coluna
- Diferencia `create` de `keep` com exemplo
- Explica impacto de cada evento no fluxo git
- Mostra relação entre gitflow configurado e gitevents

---

## CT-005 — Exemplos com melhor clareza: Exemplo Prático de Board

**Tipo:** manual
**Critério de aceitação:** Exemplos com melhor clareza

**Pré-condição:**
- Seção de exemplo prático existe (ex: "Exemplo Prático: Board User Stories")
- Exemplo mostra configuração YAML de um board completo

**Passos:**
1. Abrir `docs/pipe-yml-config/04-boards-e-colunas.md`
2. Localizar exemplo prático de board
3. Verificar se exemplo contém:
   - Estrutura completa de um board com múltiplas colunas
   - Anotações explicando cada campo
   - Fluxo visível de uma issue: backlog → validação → desenvolvimento → concluído
   - Comportamento esperado em cada coluna
4. Tentar seguir exemplo como iniciante

**Resultado esperado:**
- Exemplo é autoexplicativo com comentários inline
- Consegue rastrear jornada de uma issue do início ao fim
- Campos estão contextualizados (por que `todo: backlog`, por que `priority: 3`)
- Clareza suficiente para copiar e adaptar para caso de uso próprio

---

## CT-006 — Exemplos com melhor clareza: Casos de Transição

**Tipo:** manual
**Critério de aceitação:** Exemplos com melhor clareza

**Pré-condição:**
- Exemplos de transições estão documentados
- Há ilustração de quando cada transição acontece

**Passos:**
1. Abrir `docs/pipe-yml-config/04-boards-e-colunas.md`
2. Localizar exemplos de transições
3. Verificar se há exemplos reais/comuns de:
   - Issue sendo aprovada (`advance`)
   - Issue sendo devolvida para revisão (`reprovar`)
   - Issue sendo rejeitada (`cancelar`)
   - Teste falhando e voltando para dev (`falha`)
4. Validar que exemplos mostram pré-condição e resultado

**Resultado esperado:**
- Exemplos mostram contexto (por que transição aconteceu)
- Fácil de entender quando cada cenário ocorre
- Deixa claro qual é a coluna destino após transição
- Ajuda a entender diferença entre reprovar e falha

---

## CT-007 — Sem quebra de conteúdo: Compatibilidade Regressiva

**Tipo:** manual
**Critério de aceitação:** Sem quebra de conteúdo existente

**Pré-condição:**
- Versão anterior de `04-boards-e-colunas.md` conhecida
- Conteúdo existente deve ser preservado

**Passos:**
1. Comparar arquivo novo com versão anterior
2. Verificar que:
   - Seções existentes não foram removidas
   - Ordem de seções foi mantida (ou melhorada com justificativa)
   - Exemplos YAML anteriores ainda funcionam
   - Campos de configuração não foram removidos/renomeados
3. Validar estrutura de índice/navegação

**Resultado esperado:**
- Nenhuma seção importante foi deletada
- Conteúdo novo foi adicionado, não substituído
- Links internos (se existem) ainda funcionam
- Documento é backward-compatible

---

## CT-008 — Aderência Arquitetural: Consistência com Documentação

**Tipo:** manual
**Critério de aceitação:** Contexto claro sobre cada configuração

**Pré-condição:**
- Outros arquivos de documentação (02, 03, 05) foram consultados
- Conceitos comuns estão alinhados

**Passos:**
1. Comparar termos e conceitos em:
   - `04-boards-e-colunas.md` (novo)
   - `02-configuracao-global.md`
   - `03-gitflows.md`
   - `05-agentes-e-esforco.md`
2. Validar alinhamento de:
   - Definição de "gitflow" em 03 vs uso em 04
   - Definição de "agent" em 05 vs uso em 04
   - Terminologia consistente entre arquivos
3. Verificar que não há contradições

**Resultado esperado:**
- Conceitos são explicados da mesma forma em todos os arquivos
- Terminologia consistente (não muda "board" para "workflow")
- Referências cruzadas entre arquivos estão corretas
- Não há conflito de informações entre seções

---

## Resumo de Casos

- **Total**: 8
- **Manuais**: 8
- **Automatizados**: 0

## Notas para Execução

- CT-001 a CT-004: Verificam expansão de explicações e clareza
- CT-005 a CT-006: Verificam qualidade de exemplos
- CT-007: Verifica regressão de conteúdo
- CT-008: Verifica consistência arquitetural com outras seções

Todos os casos dependem de análise manual do documento. Executar sequencialmente lendo o arquivo inteiro.
