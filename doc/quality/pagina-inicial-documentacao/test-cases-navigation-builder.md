# Casos de Teste — Criar Componente Navigation Builder

Status: approved
Owner: quality
Last updated: 2026-06-22

## Inputs
- Task 81: Criar componente Navigation Builder
- User Story 49: Página Inicial de Documentação
- Critério de aceite: Estrutura de navegação para 3 personas, validação ≤3 cliques, ≥5 atalhos, testes de estrutura plana/aninhada

## CT-001 — Construção de Árvore para Persona Iniciante

**Tipo:** unitário
**Critério de aceitação:** Estrutura de navegação criada para 3 personas (iniciante, avançado, desenvolvedor)

**Pré-condição:**
- Content Aggregator retorna índice com metadados para 15+ documentos
- Cada documento contém campo `personas: ["iniciante", "avançado", "desenvolvedor"]` no frontmatter
- NavBuilder inicializado com índice válido

**Passos:**
1. Invocar `NavBuilder.build_tree(index, persona="iniciante")`
2. Validar que árvore contém apenas documentos onde `"iniciante"` está em `personas`
3. Verificar que profundidade máxima é 3 níveis

**Resultado esperado:**
- Retorna dict/object com estrutura: `{"sections": [...], "depth": int, "shortcuts": [...]}`
- Todos os itens na árvore têm `personas` contendo "iniciante"
- Profundidade máxima ≤ 3

## CT-002 — Validação do Limite de 3 Cliques

**Tipo:** unitário
**Critério de aceitação:** Validação garante ≤3 cliques para qualquer seção

**Pré-condição:**
- Árvore construída para persona (CT-001 resultado)
- Método `validate_depth()` disponível

**Passos:**
1. Para cada folha na árvore, contar número de cliques do root até folha
2. Invocar `NavBuilder.validate_depth(tree, max_depth=3)`
3. Verificar se retorna `True` ou lista de violações

**Resultado esperado:**
- `validate_depth()` retorna `True` se todas as folhas estão a ≤3 cliques do root
- Se alguma seção viola limite, retorna `False` com lista de violações
- Nenhuma seção está a mais de 3 cliques

## CT-003 — Mapeamento de Atalhos (5+ Casos de Uso)

**Tipo:** unitário
**Critério de aceitação:** Atalhos mapeados para 5+ casos de uso comuns

**Pré-condição:**
- Árvore construída (CT-001 resultado)
- Arquivo de configuração de atalhos: `shortcuts.yaml` contendo ≥5 casos de uso

**Passos:**
1. Invocar `NavBuilder.build_shortcuts(tree, shortcuts_config)`
2. Validar que cada atalho tem: `id`, `label`, `description`, `paths` (array de caminhos)
3. Verificar que todos os atalhos resolvem para seções válidas na árvore

**Resultado esperado:**
- Retorna dict com ≥5 shortcuts
- Cada shortcut tem estrutura válida: `{"id": str, "label": str, "description": str, "paths": [str, ...]}`
- Todos os paths são alcançáveis na árvore (≤3 cliques)
- Exemplos: "instalacao", "configuracao-basica", "criar-story", "troubleshooting", "contribuir"

## CT-004 — Teste de Estrutura Plana

**Tipo:** integração
**Critério de aceitação:** Testes: estrutura plana

**Pré-condição:**
- Índice contém documentos de estrutura plana (todos em nível 1, nenhuma hierarquia)
- Ex: 10 docs independentes, sem relações parent-child

**Passos:**
1. Invocar `NavBuilder.build_tree(flat_index, persona="avançado")`
2. Validar que resultado contém lista de 10 seções em profundidade 1
3. Verificar que `validate_depth()` passa

**Resultado esperado:**
- Árvore retorna estrutura simples: `{"sections": [{"title": ..., "id": ...}, ...], "depth": 1}`
- Todos os 10 docs aparecem na primeira camada
- Validação de profundidade passa

## CT-005 — Teste de Estrutura Aninhada (3 Níveis)

**Tipo:** integração
**Critério de aceitação:** Testes: estrutura aninhada

**Pré-condição:**
- Índice contém documentos com hierarquia: seção → subsection → artigo
- Exemplo: "Guia" (nível 1) → "Instalação" (nível 2) → "Linux" (nível 3)
- Documentos contêm `parent_id` para navegação hierárquica

**Passos:**
1. Invocar `NavBuilder.build_tree(hierarchical_index, persona="desenvolvedor")`
2. Validar que árvore respeita hierarquia: items de nível 2 estão sob nível 1
3. Verificar profundidade máxima = 3
4. Invocar `validate_depth()` e verificar resultado

**Resultado esperado:**
- Árvore tem 3 camadas: root → categories → articles
- Hierarquia é preservada: items filhos aparecem dentro de `children` dos pais
- Validação retorna `True`
- Exemplo: `tree["sections"][0]["children"][0]["children"][0]` é acessível

## CT-006 — Detecção de Violação de Profundidade

**Tipo:** unitário
**Critério de aceitação:** Testes: limite de 3 cliques (violação)

**Pré-condição:**
- Índice contém documentos com hierarquia > 3 níveis (violação do limite)
- Exemplo: Nível 1 → 2 → 3 → 4

**Passos:**
1. Invocar `NavBuilder.build_tree(deep_index, persona="iniciante")`
2. Invocar `validate_depth(tree, max_depth=3)`
3. Capturar resultado e mensagem de erro

**Resultado esperado:**
- `validate_depth()` retorna `False`
- Retorna lista de violações com caminho: `["Seção > SubseçãoA > SubseçãoB > ArticuloC", ...]`
- Cada violação indica quantidade de cliques (4+)

## CT-007 — Sem Duplicação de Links

**Tipo:** unitário
**Critério de aceitação:** Sem duplicação de links no mapa de navegação

**Pré-condição:**
- Índice contém documentos, alguns com múltiplas personas
- Ex: documento X contém `personas: ["iniciante", "avançado"]`

**Passos:**
1. Invocar `NavBuilder.build_tree(index, persona="iniciante")`
2. Contar ocorrências de cada `doc_id` na árvore
3. Verificar que nenhum doc_id aparece mais de 1 vez

**Resultado esperado:**
- Cada documento aparece apenas 1 vez na árvore
- Não há links duplicados
- Se houver cross-linking, é representado como referência única, não duplicação

## CT-008 — Atalhos Resolvem Corretamente

**Tipo:** integração
**Critério de aceitação:** Atalhos para casos de uso comuns resolvem para seções válidas

**Pré-condição:**
- Árvore construída com ≥5 shortcuts (CT-003)
- Cada shortcut tem array `paths` com caminhos alternativos

**Passos:**
1. Para cada shortcut, invocar `NavBuilder.resolve_shortcut(shortcut_id, tree)`
2. Verificar que resultado retorna seção válida da árvore
3. Validar que todos os caminhos alternativos resolvem para mesma seção

**Resultado esperado:**
- Cada shortcut resolve para seção válida
- Se shortcut tem múltiplos paths, todos resolvem para mesmo `doc_id`
- Cada shortcut está a ≤3 cliques do root

## CT-009 — Cross-linking Sem Duplicação

**Tipo:** integração
**Critério de aceitação:** Suporta cross-linking entre seções sem duplicação

**Pré-condição:**
- Índice contém documento A com referência cruzada para documento B
- Ex: A `references: [B_id]` no frontmatter
- Ambos A e B estão em mesma persona

**Passos:**
1. Invocar `NavBuilder.build_tree(index_with_refs, persona)`
2. Localizar posição de A e B na árvore
3. Validar que ambos aparecem 1 vez cada
4. Verificar se cross-link é representado como campo `related` ou similar, não como nó duplicado

**Resultado esperado:**
- A aparece em posição original na árvore
- B aparece em posição original na árvore
- A contém campo `related: [{"id": B_id, "title": B_title}]` (ou similar)
- Nenhuma duplicação de nós

## CT-010 — Builder Rejeita Índice Inválido

**Tipo:** unitário
**Critério de aceitação:** Validação de índice de entrada

**Pré-condição:**
- Índice com dados malformados ou ausentes
- Exemplos: falta campo `personas`, `parent_id` referencia doc inexistente, ciclo de referências

**Passos:**
1. Invocar `NavBuilder.build_tree(invalid_index, persona="iniciante")`
2. Capturar exceção ou código de erro retornado
3. Verificar mensagem de validação

**Resultado esperado:**
- Levanta `ValueError` ou retorna `{"error": "message", "details": [...]}`
- Mensagem claramente indica o problema: "Missing personas field in doc X", "Invalid parent_id in doc Y", etc.
- Execução não prossegue com dados inválidos
