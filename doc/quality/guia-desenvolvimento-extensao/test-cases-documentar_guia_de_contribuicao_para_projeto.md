# Casos de Teste — Documentar Guia de Contribuição para Projeto

Status: draft
Owner: quality
Last updated: 2026-06-17

## Inputs
- #50 — Guia de Desenvolvimento e Extensão
- #110 — Documentar Guia de Contribuição para Projeto

## CT-001 — Guia de Contribuição contém seção com fluxo fork → branch → PR → merge

**Tipo:** integração
**Critério de aceitação:** Documentação contém seção "Guia de Contribuição" e explica fluxo

**Pré-condição:**
- Arquivo `doc/guias/guia-contribuicao.md` existe
- Arquivo está acessível e formatado em markdown

**Passos:**
1. Abrir arquivo de guia de contribuição
2. Procurar seção "Fluxo de Contribuição" ou equivalente
3. Verificar presença de: fork, branch, PR, merge
4. Validar que cada etapa tem descrição clara

**Resultado esperado:**
- Seção existe com todas as 4 etapas descritas
- Ordem está correta: fork → branch → PR → merge
- Cada etapa tem pelo menos 1 frase explicativa

---

## CT-002 — Guia inclui checklist de antes de PR com testes, lint e docs

**Tipo:** integração
**Critério de aceitação:** Inclui checklist de antes de PR (testes, lint, docs)

**Pré-condição:**
- Arquivo de guia de contribuição está criado

**Passos:**
1. Procurar seção "Checklist de Antes de PR" ou equivalente
2. Verificar presença de: testes, lint, documentação

**Resultado esperado:**
- Checklist existe com no mínimo 3 itens
- Contém validação de: testes passando, lint sem erros, docs atualizadas
- Itens são claros e acionáveis

---

## CT-003 — Guia referencia padrões de branch naming e commit message

**Tipo:** integração
**Critério de aceitação:** Referencia padrões (branch naming, commit message)

**Pré-condição:**
- Arquivo de guia de contribuição está criado

**Passos:**
1. Procurar seção sobre padrões de naming ou convenções
2. Verificar presença de: convenção de branch naming, padrão de commit message

**Resultado esperado:**
- Seção sobre padrões existe
- Inclui exemplo de branch name (ex: feature/issue-123-descricao)
- Inclui exemplo de commit message com formato esperado
- Referencia padrão estabelecido no projeto

---

## CT-004 — Guia explica processo de reportar issues com seção dedicada

**Tipo:** integração
**Critério de aceitação:** Seção explicando como reportar e documentar um issue

**Pré-condição:**
- Arquivo de guia de contribuição está criado

**Passos:**
1. Procurar seção sobre reportar issues
2. Verificar conteúdo da seção

**Resultado esperado:**
- Seção "Como Reportar Issues" ou equivalente existe
- Explica campos obrigatórios: descrição, passos para reproduzir, resultado esperado
- Inclui exemplo de issue bem formado

---

## CT-005 — Guia menciona escopo: núcleo da esteira + integrações externas

**Tipo:** integração
**Critério de aceitação:** Menciona escopo: núcleo da esteira + integrações externas

**Pré-condição:**
- Arquivo de guia de contribuição está criado

**Passos:**
1. Procurar seção sobre escopo de contribuição ou áreas do projeto
2. Verificar menção a: núcleo da esteira, integrações externas

**Resultado esperado:**
- Seção "Escopo de Contribuição" ou equivalente existe
- Diferencia entre núcleo (esteira) e extensões (integrações)
- Explica como contribuir em cada área

---

## CT-006 — Arquivo está em `doc/guias/guia-contribuicao.md` ou similar

**Tipo:** integração
**Critério de aceitação:** Arquivo em `doc/guias/guia-contribuicao.md` ou similar

**Pré-condição:**
- Build do projeto completou

**Passos:**
1. Verificar existência do arquivo no caminho correto
2. Validar que está em formato markdown
3. Verificar referência no índice principal de docs

**Resultado esperado:**
- Arquivo existe em `doc/guias/guia-contribuicao.md` (ou variação clara)
- Está em formato markdown válido
- É referenciado no índice/README da documentação

---

## CT-007 — Guia menciona como rodar testes localmente

**Tipo:** integração
**Critério de aceitação:** Seção: Como rodar testes localmente

**Pré-condição:**
- Arquivo de guia de contribuição está criado

**Passos:**
1. Procurar seção sobre testes
2. Verificar instruções para rodar testes

**Resultado esperado:**
- Seção "Como Rodar Testes" existe
- Inclui comando exato para rodar todos os testes
- Inclui comando para rodar testes específicos
- Menciona ferramenta/framework de testes usada

---

## CT-008 — Guia menciona padrões de código esperados (lint, testes, docs)

**Tipo:** integração
**Critério de aceitação:** Seção: Padrões de código esperados

**Pré-condição:**
- Arquivo de guia de contribuição está criado

**Passos:**
1. Procurar seção sobre padrões de código
2. Verificar menção de: lint, testes, documentação

**Resultado esperado:**
- Seção "Padrões de Código" existe
- Explica configuração de lint (ferramenta e arquivo de config)
- Menciona cobertura de testes esperada
- Explica documentação esperada (docstrings, comments)

---

## CT-009 — Documentação não contém configuração específica de ambientes

**Tipo:** integração
**Critério de aceitação:** Fora de escopo: Configuração de ambientes de desenvolvimento específicos

**Pré-condição:**
- Arquivo de guia de contribuição está criado

**Passos:**
1. Procurar seções sobre setup de ambiente
2. Verificar se contém instruções específicas de OS (Windows, MacOS, Linux)
3. Verificar se contém instruções de IDE específica

**Resultado esperado:**
- Guia não contém instruções de setup de ambiente específicas
- Se houver setup mínimo necessário, é referenciado brevemente
- Detalhe de setup é deixado para documentação de setup específica

---

## CT-010 — Documentação mantém coesão com outras seções do guia (arquitetura, debugging)

**Tipo:** integração
**Critério de aceitação:** Guia é coeso com outras partes da documentação técnica

**Pré-condição:**
- Arquivo de guia de contribuição está criado
- Outros documentos técnicos existem (arquitetura, debugging)

**Passos:**
1. Ler guia de contribuição
2. Verificar referências cruzadas para: arquitetura, debugging
3. Validar consistência de terminologia e conceitos

**Resultado esperado:**
- Terminologia é consistente com documentação de arquitetura
- Referências a outras seções funcionam logicamente
- Não contém instruções duplicadas de outras seções