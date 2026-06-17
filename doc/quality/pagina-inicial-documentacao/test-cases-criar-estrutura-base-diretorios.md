# Casos de Teste — Criar estrutura base de diretórios em /doc

Status: draft
Owner: quality
Last updated: 2026-06-16

## Inputs
- Task: 79 - Criar estrutura base de diretórios em /doc
- User Story: 49 - Página Inicial de Documentação

## CT-001 — Diretórios requeridos existem

**Tipo:** unitário
**Critério de aceitação:** Diretórios criados conforme estrutura definida

**Pré-condição:**
- Repositório em estado limpo na branch feature/79

**Passos:**
1. Verificar existência de `/doc/iniciante/`
2. Verificar existência de `/doc/avancado/`
3. Verificar existência de `/doc/desenvolvedor/`
4. Verificar existência de `/doc/casos-uso/`

**Resultado esperado:**
- Todos os 4 diretórios existem e são acessíveis

## CT-002 — README.md em cada diretório

**Tipo:** unitário
**Critério de aceitação:** Cada diretório contém README.md com descrição clara

**Pré-condição:**
- Diretórios criados (CT-001 passou)

**Passos:**
1. Verificar existência de `/doc/iniciante/README.md`
2. Verificar existência de `/doc/avancado/README.md`
3. Verificar existência de `/doc/desenvolvedor/README.md`
4. Verificar existência de `/doc/casos-uso/README.md`

**Resultado esperado:**
- Todos os 4 arquivos README.md existem

## CT-003 — README.md contém descrição

**Tipo:** unitário
**Critério de aceitação:** README.md com descrição clara e lista de links esperados

**Pré-condição:**
- README.md em cada diretório (CT-002 passou)

**Passos:**
1. Ler `/doc/iniciante/README.md` e verificar se contém descrição
2. Ler `/doc/avancado/README.md` e verificar se contém descrição
3. Ler `/doc/desenvolvedor/README.md` e verificar se contém descrição
4. Ler `/doc/casos-uso/README.md` e verificar se contém descrição

**Resultado esperado:**
- Cada README contém descrição clara da seção
- Cada README contém lista de links internos esperados (mesmo que vazia inicialmente)

## CT-004 — Localizar guia rápido como usuário iniciante

**Tipo:** integração
**Critério de aceitação:** Dado que sou novo no projeto, quando acesso a documentação, então encontro rapidamente o guia de instalação

**Pré-condição:**
- Estrutura criada (CT-001 passou)
- README.md em `/doc/iniciante/` contém referência a guia de instalação

**Passos:**
1. Acessar `/doc/iniciante/README.md`
2. Procurar por link ou referência a "instalação" ou "guia de instalação"

**Resultado esperado:**
- Link ou referência a guia de instalação está presente em `/doc/iniciante/`

## CT-005 — Navegação para documentação avançada

**Tipo:** integração
**Critério de aceitação:** Dado que sou usuário experiente, quando busco configurações específicas, então navego diretamente para documentação avançada

**Pré-condição:**
- Estrutura criada (CT-001 passou)
- `/doc/avancado/README.md` contém orientações

**Passos:**
1. Acessar `/doc/avancado/README.md`
2. Verificar se contém descrição de configurações avançadas
3. Verificar se há links organizados por tópico

**Resultado esperado:**
- `/doc/avancado/` está estruturado para usuários experientes
- Descrição clara do conteúdo esperado

## CT-006 — Localizar guia de desenvolvimento

**Tipo:** integração
**Critério de aceitação:** Dado que sou desenvolvedor, quando quero contribuir, então encontro facilmente o guia de desenvolvimento

**Pré-condição:**
- Estrutura criada (CT-001 passou)
- `/doc/desenvolvedor/README.md` contém orientações

**Passos:**
1. Acessar `/doc/desenvolvedor/README.md`
2. Verificar se contém descrição do desenvolvimento/contribuição

**Resultado esperado:**
- `/doc/desenvolvedor/` está estruturado com foco em contribuição
- Descrição clara do propósito

## CT-007 — Segregação por persona

**Tipo:** unitário
**Critério de aceitação:** Estrutura segue padrão de segregação por persona

**Pré-condição:**
- Estrutura criada (CT-001 passou)

**Passos:**
1. Verificar se existem diretórios separados para `iniciante`, `avancado`, `desenvolvedor`
2. Verificar se há diretório para `casos-uso`

**Resultado esperado:**
- Estrutura permite clara segregação por tipo de usuário
- Cada persona tem seu espaço definido

## CT-008 — Sem quebra de funcionalidades existentes

**Tipo:** integração
**Critério de aceitação:** Sem quebra de funcionalidades existentes

**Pré-condição:**
- Repositório em estado limpo antes da mudança

**Passos:**
1. Verificar se existem outros arquivos em `/doc` antes da task
2. Após criar estrutura, verificar se todos permanecem acessíveis
3. Executar build/testes existentes (se houver)

**Resultado esperado:**
- Nenhum arquivo existente foi removido ou corrompido
- Build/testes continuam passando
