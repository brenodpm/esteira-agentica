# Casos de Teste — Criar componente Content Aggregator

Status: draft
Owner: quality
Last updated: 2026-06-16

## Inputs
- User Story 49: Página Inicial de Documentação
- Task 80: Criar componente Content Aggregator

## CT-001 — Leitura recursiva de arquivos em /doc

**Tipo:** unitário
**Critério de aceitação:** Componente lê arquivos de `/doc` recursivamente

**Pré-condição:**
- Estrutura `/doc` existe com arquivos Markdown aninhados em subdiretórios
- Componente Content Aggregator implementado

**Passos:**
1. Inicializar Content Aggregator
2. Chamar método de leitura de `/doc`
3. Verificar se arquivos em `/doc/subdir/arquivo.md` são detectados

**Resultado esperado:**
- Componente retorna lista com todos os arquivos `.md` encontrados em qualquer profundidade sob `/doc`
- Total de arquivos detectados ≥ número de arquivos presentes

---

## CT-002 — Extração de frontmatter YAML válido

**Tipo:** unitário
**Critério de aceitação:** Extrai frontmatter conforme convenção definida

**Pré-condição:**
- Arquivo com frontmatter YAML válido (entre `---`)
- Frontmatter contém: título, descrição, personas, tags

**Passos:**
1. Fornecer arquivo com frontmatter YAML válido
2. Chamar método de extração de frontmatter
3. Parsear campos: title, description, personas, tags

**Resultado esperado:**
- Frontmatter extraído com sucesso
- Campos individuais acessíveis e tipados corretamente
- Nenhuma exceção lançada

---

## CT-003 — Arquivo sem frontmatter

**Tipo:** unitário
**Critério de aceitação:** Cobertura de testes para casos - arquivo sem frontmatter

**Pré-condição:**
- Arquivo Markdown sem frontmatter (começa direto com `#`)

**Passos:**
1. Fornecer arquivo sem frontmatter
2. Chamar método de extração de frontmatter
3. Verificar comportamento do componente

**Resultado esperado:**
- Componente não lança exceção
- Retorna metadados padrão ou marcador de ausência
- Arquivo é registrado no índice com status "sem_metadados"

---

## CT-004 — Frontmatter mal formado

**Tipo:** unitário
**Critério de aceitação:** Cobertura de testes para casos - frontmatter mal formado

**Pré-condição:**
- Arquivo com frontmatter YAML inválido (sintaxe quebrada, chaves mal fechadas)

**Passos:**
1. Fornecer arquivo com frontmatter mal formado
2. Chamar método de extração
3. Verificar resposta do componente

**Resultado esperado:**
- Componente não crasheia
- Erro é capturado e registrado (sem propagação não-tratada)
- Arquivo é marcado como "frontmatter_inválido" no índice

---

## CT-005 — Índice estruturado por persona

**Tipo:** integração
**Critério de aceitação:** Retorna índice estruturado por persona

**Pré-condição:**
- Múltiplos arquivos com personas: "iniciante", "avançado", "desenvolvedor"
- Frontmatter válido em cada arquivo

**Passos:**
1. Processar conjunto de arquivos com personas diferentes
2. Chamar método de geração de índice
3. Verificar estrutura de retorno

**Resultado esperado:**
- Índice retorna objeto com chaves: "iniciante", "avançado", "desenvolvedor"
- Cada persona contém array de referências aos seus arquivos
- Referências incluem: caminho, título, descrição, tags

---

## CT-006 — Performance com 100 seções

**Tipo:** integração
**Critério de aceitação:** Performance: ≤500ms para 100 seções

**Pré-condição:**
- Estrutura `/doc` contém exatamente 100 arquivos Markdown com frontmatter válido
- Componente implementado

**Passos:**
1. Iniciar cronômetro
2. Chamar método de leitura e indexação completa
3. Registrar tempo decorrido

**Resultado esperado:**
- Execução completa ≤ 500ms
- Índice gerado sem erros
- Nenhuma timeout ou travamento

---

## CT-007 — Validação de integridade de metadados

**Tipo:** unitário
**Critério de aceitação:** Validar integridade de metadados

**Pré-condição:**
- Arquivo com frontmatter contendo campos obrigatórios e opcionais
- Regras de validação definidas

**Passos:**
1. Fornecer arquivo com frontmatter
2. Chamar método de validação
3. Verificar se campos obrigatórios estão presentes

**Resultado esperado:**
- Validação retorna status de integridade (válido/inválido)
- Campos obrigatórios (título, descrição) presentes em arquivo válido
- Campo persona valida contra lista permitida: ["iniciante", "avançado", "desenvolvedor"]

---

## CT-008 — Arquivos aninhados em múltiplos níveis

**Tipo:** integração
**Critério de aceitação:** Cobertura de testes para casos - arquivos aninhados

**Pré-condição:**
- Estrutura: `/doc/level1/level2/level3/arquivo.md`
- Múltiplos níveis de profundidade

**Passos:**
1. Criar estrutura aninhada
2. Chamar leitura recursiva
3. Verificar detecção de arquivo profundo

**Resultado esperado:**
- Arquivo em level3 é detectado e indexado
- Caminho completo preservado no índice
- Nenhum limite artificial de profundidade impedindo detecção
