# Casos de Teste — Implementar Navigation Builder

Status: approved
Owner: quality
Last updated: 2026-06-16

## Inputs
- User Story: [49-pagina_inicial_de_documentacao](../../../.pipe/boards/story/change-file/49-pagina_inicial_de_documentacao.md)
- Task: 75-implementar_navigation_builder
- ADR-001: Estrutura de Navegação por Perfil de Usuário
- Regras de Negócio: RN-001 a RN-006

## CT-001 — Agrupamento básico por persona

**Tipo:** unitário
**Critério de aceitação:** Agrupa seções por persona seguindo ADR-001

**Pré-condição:**
- Módulo `navigation_builder.py` importável
- Input contém lista de seções com campo `persona` preenchido
- Personas válidas: "iniciante", "avançado", "desenvolvedor"

**Passos:**
1. Criar instância de NavigationBuilder
2. Passar lista de seções com 3 personas diferentes
3. Chamar método `build()` ou equivalente
4. Verificar saída estruturada por persona

**Resultado esperado:**
- Retorna estrutura com chaves: `"iniciante"`, `"avançado"`, `"desenvolvedor"`
- Cada chave contém lista de seções associadas àquela persona
- Nenhuma seção duplicada entre personas

## CT-002 — Hierarquia respeitando limite de 3 níveis

**Tipo:** unitário
**Critério de aceitação:** Respeita limite de 3 cliques (máximo 3 níveis)

**Pré-condição:**
- Input contém seções com campos: `persona`, `category`, `title`
- Seções têm profundidade variada (1-4 níveis)

**Passos:**
1. Invocar NavigationBuilder com seções de profundidade 4
2. Chamar método `build()`
3. Verificar estrutura hierárquica resultante
4. Contar profundidade máxima

**Resultado esperado:**
- Profundidade máxima da hierarquia = 3 níveis (Persona → Categoria → Seção)
- Nenhuma seção fica a 4+ níveis de profundidade
- Estrutura JSON-compatível segue padrão: `{persona: {category: [seção]}}`

## CT-003 — Identificação de casos de uso comuns

**Tipo:** unitário
**Critério de aceitação:** Identifica e segrega casos de uso comuns

**Pré-condição:**
- Input contém seções com campo `tags` ou marcação de "common_use_case"
- Algumas seções aparecem marcadas como caso de uso comum

**Passos:**
1. Configurar NavigationBuilder com base de seções
2. Invocar método de identificação de casos de uso
3. Extrair grupo de casos de uso comuns
4. Verificar que estão segregados na estrutura final

**Resultado esperado:**
- Casos de uso comuns formam grupo separado ou destacado
- Não são removidos de suas categorias originais (referência mantida)
- Grupo de "casos de uso comuns" acessível em máximo 1 clique da raiz

## CT-004 — Estrutura JSON-compatível

**Tipo:** unitário
**Critério de aceitação:** Retorna estrutura JSON-compatível para template renderer

**Pré-condição:**
- NavigationBuilder completo
- Output será consumido por Template Renderer

**Passos:**
1. Chamar método `build()` e capturar resultado
2. Tentar fazer parse do resultado como JSON válido
3. Validar presença de campos esperados

**Resultado esperado:**
- Resultado é string JSON válida (ou dict Python que pode ser serializado)
- Contém estrutura hierárquica com keys: `personas`, `categories`, `sections`
- Cada seção contém: `title`, `url`, `persona`, `order`
- Sem caracteres inválidos ou escaping incorreto

## CT-005 — Entrada vazia

**Tipo:** unitário
**Critério de aceitação:** Comportamento bem-definido para entrada vazia

**Pré-condição:**
- NavigationBuilder inicializado
- Input é lista vazia

**Passos:**
1. Chamar `build()` com lista vazia
2. Capturar resultado

**Resultado esperado:**
- Retorna estrutura vazia ou com personas vazias (não erro/exceção)
- Resultado é JSON válido (estrutura bem-formada mas sem conteúdo)

## CT-006 — Seções sem persona definida

**Tipo:** unitário
**Critério de aceitação:** Trata seções sem persona de forma consistente

**Pré-condição:**
- Input contém seções com campo `persona` vazio/null/undefined
- Input contém 3+ seções válidas e 2+ sem persona

**Passos:**
1. Invocar `build()` com lista mista
2. Verificar onde seções sem persona acabam na estrutura

**Resultado esperado:**
- Seções sem persona vão para grupo `"unclassified"` ou `"other"` (comportamento documentado)
- Não quebram o build (tratamento gracioso)
- Aparecem no output para não serem perdidas

## CT-007 — Personas inválidas

**Tipo:** unitário
**Critério de aceitação:** Rejeita ou trata personas inválidas (validação)

**Pré-condição:**
- Validação de entrada é responsabilidade do NavigationBuilder ou Content Aggregator
- Input contém personas: "iniciante", "invalid_persona", "avançado"

**Passos:**
1. Invocar `build()` com personas inválidas
2. Capturar comportamento (erro, warning, ou coerção)

**Resultado esperado:**
- Se validação é responsabilidade deste componente: levanta ValueError com mensagem clara
- Se validação é upstream (Content Aggregator): aceita e inclui (não é responsabilidade deste)
- Comportamento deve ser testável e documentado na docstring

## CT-008 — Ordem de seções preservada

**Tipo:** unitário
**Critério de aceitação:** Respeita campo `order` para ordenação

**Pré-condição:**
- Input contém seções com campo `order` (inteiros 1, 2, 3...)
- Ordens não estão sequenciais na entrada (embaralhadas)

**Passos:**
1. Invocar `build()` com seções embaralhadas por ordem
2. Verificar estrutura resultante

**Resultado esperado:**
- Seções aparecem ordenadas por campo `order` dentro de cada categoria
- Ordem é respeitada em níveis Categoria e Seção
- Sem alteração de ordem de input, mantém ordem de entrada (estável)

## CT-009 — Cobertura de todos os critérios de aceitação

**Tipo:** integração
**Critério de aceitação:** Cobertura completa dos 6 critérios da task

**Pré-condição:**
- Suite de testes unitários executada
- Coverage report gerado

**Passos:**
1. Executar: `pytest tests/test_navigation_builder.py -v --cov=src.navigation_builder --cov-report=term-missing`
2. Verificar que cada critério tem pelo menos um teste associado
3. Conferir linhas de cobertura

**Resultado esperado:**
- ✅ Módulo `navigation_builder.py` criado e funcional → CT-001 a CT-008
- ✅ Agrupa seções por persona → CT-001
- ✅ Respeita limite de 3 cliques → CT-002
- ✅ Identifica e segrega casos de uso comuns → CT-003
- ✅ Testes unitários cobrem agrupamento e hierarquia → CT-001, CT-002, CT-008
- ✅ Cobertura ≥ 80% do código do módulo

## CT-010 — Sem quebra de funcionalidades existentes

**Tipo:** integração
**Critério de aceitação:** Nenhuma quebra de funcionalidades existentes

**Pré-condição:**
- Suite de testes do projeto executada
- Novos imports de `navigation_builder` adicionados ao sistema

**Passos:**
1. Executar: `pytest tests/ -v`
2. Verificar que testes existentes continuam passando
3. Validar nenhum ImportError relacionado a novo módulo

**Resultado esperado:**
- Todos os testes preexistentes continuam passando
- Nenhuma alteração em módulos existentes (exceto imports se necessário)
- Build do projeto não é afetado

## CT-011 — Aderência arquitetural: Input vs Output

**Tipo:** arquitetura
**Critério de aceitação:** Validar contrato com Content Aggregator e Template Renderer

**Pré-condição:**
- Saída do Content Aggregator está disponível
- Especificação do input de Template Renderer está documentada

**Passos:**
1. Verificar que input esperado por NavigationBuilder coincide com output do Content Aggregator
2. Verificar que output de NavigationBuilder é compatível com input de Template Renderer
3. Verificar que não há transformações desnecessárias ou perda de dados

**Resultado esperado:**
- ✅ Input: lista de seções com campos `{title, persona, category, order, url}`
- ✅ Output: estrutura hierárquica `{persona: {category: [{seção}]}}`
- ✅ Compatibilidade mantida (sem breaking changes)
- ✅ Nenhuma violação de camadas (NavigationBuilder não renderiza HTML, não valida links, etc)

## CT-012 — Casos de uso comuns identificados corretamente

**Tipo:** integração
**Critério de aceitação:** Identificação correta de 5-7 casos de uso principais (RN-005)

**Pré-condição:**
- Casos de uso principais estão marcados na entrada (tag ou campo dedicado)
- Esperados: instalação, configuração básica, criar story, troubleshooting, etc

**Passos:**
1. Invocar `build()` com seções marcadas como casos de uso comuns
2. Extrair grupo de casos de uso do output
3. Verificar que aparecem no máximo 1 clique da raiz

**Resultado esperado:**
- Casos de uso comuns aparecem em estrutura separada ou destacada
- Nenhum caso de uso comum fica enterrado a mais de 2 níveis
- Acessíveis em ≤ 1 clique a partir da página inicial

