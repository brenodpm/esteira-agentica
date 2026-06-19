# Casos de Teste — Implementar Content Aggregator

Status: approved
Owner: quality
Last updated: 2026-06-19

## Inputs
- [Task 74: Implementar Content Aggregator](/home/breno/pipes/esteira-agentica/.pipe/boards/task/execucao-testes/74-implementar_content_aggregator.md)
- [User Story 49: Página Inicial de Documentação](/home/breno/pipes/esteira-agentica/.pipe/boards/story/concluido/49-pagina_inicial_de_documentacao.md)

## CT-001 — Módulo doc_scanner.py existe e é importável

**Tipo:** unitário
**Critério de aceitação:** Módulo `doc_scanner.py` criado e funcional

**Pré-condição:**
- Projeto setupado com dependências instaladas
- Arquivo `src/doc_scanner.py` presente

**Passos:**
1. Importar `DocScanner` de `src.doc_scanner`
2. Instanciar classe com caminho válido
3. Verificar se classe tem método `scan()`

**Resultado esperado:**
- Importação sem erros
- Classe instanciável
- Método `scan()` acessível

## CT-002 — Lê recursivamente arquivos .md em diretórios

**Tipo:** unitário
**Critério de aceitação:** Lê recursivamente arquivos `.md` em `/docs`

**Pré-condição:**
- DocScanner importado e instanciado
- Diretório temporário com estrutura: `root.md` e `subdir/sub.md`

**Passos:**
1. Criar DocScanner apontando para diretório raiz
2. Executar `scan()`
3. Contar documentos retornados

**Resultado esperado:**
- Retorna 2 documentos (raiz e subdiretório)
- Ambos têm chave `file_path` com caminho correto

## CT-003 — Extrai frontmatter YAML com todos campos obrigatórios

**Tipo:** unitário
**Critério de aceitação:** Extrai frontmatter YAML com campos obrigatórios (title, persona, category, order)

**Pré-condição:**
- DocScanner instanciado
- Arquivo MD com frontmatter válido:
  ```yaml
  ---
  title: "Test Document"
  persona: developer
  category: guide
  order: 1
  ---
  ```

**Passos:**
1. Criar arquivo MD com frontmatter válido
2. Executar `scan()`
3. Verificar documento retornado

**Resultado esperado:**
- Documento contém: `title`, `persona`, `category`, `order`
- Valores coincidem com frontmatter
- `file_path` está presente

## CT-004 — Registra warnings para arquivos sem frontmatter

**Tipo:** unitário
**Critério de aceitação:** Validar frontmatter obrigatório; registrar warnings para arquivos sem frontmatter

**Pré-condição:**
- DocScanner instanciado
- Arquivo MD **sem** frontmatter

**Passos:**
1. Criar arquivo MD sem frontmatter
2. Executar `scan()`
3. Verificar lista `warnings` da instância

**Resultado esperado:**
- Arquivo NÃO retornado em resultado
- `scanner.warnings` contém 1 entrada
- Mensagem refere "no frontmatter"

## CT-005 — Valida campos obrigatórios do frontmatter

**Tipo:** unitário
**Critério de aceitação:** Validar frontmatter obrigatório

**Pré-condição:**
- DocScanner instanciado
- Arquivo MD com frontmatter **incompleto** (faltam campos como `persona`)

**Passos:**
1. Criar arquivo MD com frontmatter faltando `persona`
2. Executar `scan()`
3. Verificar resultado e warnings

**Resultado esperado:**
- Arquivo NÃO retornado
- `scanner.warnings` contém 1 entrada
- Mensagem refere "missing required fields"

## CT-006 — Nenhuma regressão em testes existentes

**Tipo:** integração
**Critério de aceitação:** Nenhuma quebra de funcionalidades existentes

**Pré-condição:**
- Codebase completo com todos os testes do projeto

**Passos:**
1. Executar `pytest tests/` com todos os casos
2. Contar testes passando/falhando

**Resultado esperado:**
- Todos os 26 testes passam
- Nenhuma falha em módulos existentes
- Exit code 0
