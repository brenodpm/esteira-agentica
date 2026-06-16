# Casos de Teste — Criar estrutura de diretórios para /docs

Status: approved
Owner: quality
Last updated: 2026-06-16

## Inputs
- Task: [73-criar_estrutura_de_diretorios_para_docs](../../.pipe/boards/task/casos-de-teste/73-criar_estrutura_de_diretorios_para_docs.md)
- User Story: [49-pagina_inicial_de_documentacao](../../.pipe/boards/story/change-file/49-pagina_inicial_de_documentacao.md)

## CT-001 — Estrutura de diretórios base criada

**Tipo:** unitário
**Critério de aceitação:** Estrutura de diretórios criada em `/docs` com subdiretórios por persona

**Pré-condição:**
- Repositório clonado
- `/docs` não existe ou está vazio

**Passos:**
1. Verificar se `/docs` existe
2. Verificar se `/docs/iniciante/` existe
3. Verificar se `/docs/avançado/` existe
4. Verificar se `/docs/desenvolvedor/` existe
5. Verificar se `/docs/casos-uso/` existe

**Resultado esperado:**
- Todos os 4 subdiretórios criados em `/docs`
- Nenhum erro ao listar os diretórios

---

## CT-002 — README.md em cada subdiretório

**Tipo:** unitário
**Critério de aceitação:** Cada subdiretório tem `README.md` explicando seu propósito

**Pré-condição:**
- Estrutura de diretórios criada conforme CT-001

**Passos:**
1. Verificar se `/docs/iniciante/README.md` existe
2. Verificar se `/docs/avançado/README.md` existe
3. Verificar se `/docs/desenvolvedor/README.md` existe
4. Verificar se `/docs/casos-uso/README.md` existe
5. Validar que cada README.md não está vazio

**Resultado esperado:**
- Todos os 4 arquivos `README.md` existem
- Cada README.md contém texto descritivo (não vazio)

---

## CT-003 — Conformidade com ADR-002

**Tipo:** integração
**Critério de aceitação:** Estrutura segue ADR-002 (convenções para auto-geração)

**Pré-condição:**
- Estrutura de diretórios criada conforme CT-001
- ADR-002 disponível em `/doc/architecture`

**Passos:**
1. Ler ADR-002 para identificar convenções de metadados
2. Verificar se os `README.md` contêm seção de metadados esperada
3. Validar que a estrutura de diretórios segue a hierarquia definida em ADR-002

**Resultado esperado:**
- Estrutura alinha-se com convenções de ADR-002
- README.md contêm comentários ou seções explicando propósito de cada diretório

---

## CT-004 — Nenhuma quebra de funcionalidades existentes

**Tipo:** integração
**Critério de aceitação:** Nenhuma quebra de funcionalidades existentes

**Pré-condição:**
- Repositório em estado limpo (sem mudanças não commitadas)
- Todos os testes da branch `epic/49-pagina_inicial_de_documentacao` passam

**Passos:**
1. Executar suite de testes do projeto
2. Verificar se algum teste falha relacionado a documentação ou estrutura
3. Validar que nenhum arquivo existente foi deletado ou sobrescrito

**Resultado esperado:**
- Suite de testes executa com sucesso
- Nenhum teste novo falha
- Nenhum arquivo existente foi modificado

---

## CT-005 — Navegação por persona (integração com critério CA-001)

**Tipo:** E2E
**Critério de aceitação:** Novo no projeto encontra rapidamente o guia de instalação (CA-001)

**Pré-condição:**
- Estrutura de diretórios criada conforme CT-001
- `/docs/iniciante/` contém arquivo de guia de instalação

**Passos:**
1. Acessar `/docs`
2. Localizar diretório `/docs/iniciante/`
3. Verificar se há arquivo relacionado a instalação

**Resultado esperado:**
- `/docs/iniciante/` é facilmente identificável
- Contém ou referencia guia de instalação

---

## CT-006 — Conformidade de estrutura de metadados

**Tipo:** unitário
**Critério de aceitação:** README.md contêm comentário sobre estrutura esperada

**Pré-condição:**
- Estrutura de diretórios criada conforme CT-001

**Passos:**
1. Ler conteúdo de `/docs/iniciante/README.md`
2. Ler conteúdo de `/docs/avançado/README.md`
3. Ler conteúdo de `/docs/desenvolvedor/README.md`
4. Ler conteúdo de `/docs/casos-uso/README.md`
5. Validar que cada arquivo contém comentário explicando estrutura esperada

**Resultado esperado:**
- Cada README.md contém descrição clara do propósito
- Explicação é legível e útil para novos colaboradores
