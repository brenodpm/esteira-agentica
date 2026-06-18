# Casos de Teste — Corrigir descrição do campo sleeptime em 02-configuracao-global.md

Status: approved
Owner: quality
Last updated: 2026-06-17

## Inputs
- Task 118: Corrigir descrição do campo sleeptime em 02-configuracao-global.md
- User Story 51: Documentação Completa do pipeyml

---

## CT-001 — Descrição atualizada para texto correto

**Tipo:** validação manual

**Critério de aceitação:** Descrição atualizada para "tempo que o agente aguarda quando não há mais o que trabalhar"

**Pré-condição:**
- Arquivo `docs/pipe-yml-config/02-configuracao-global.md` aberto

**Passos:**
1. Localizar a seção "Campo: pipe.agent.sleeptime" no arquivo
2. Verificar o conteúdo do parágrafo descritivo
3. Comparar com o texto esperado

**Resultado esperado:**
- Descrição contém exatamente: "tempo que o agente aguarda quando não há mais o que trabalhar"
- Ou formulação equivalente que transmita o mesmo conceito

---

## CT-002 — Exemplo YAML mantém coerência

**Tipo:** validação manual

**Critério de aceitação:** Documentação permanece coerente com o resto do arquivo

**Pré-condição:**
- Arquivo `docs/pipe-yml-config/02-configuracao-global.md` aberto
- CT-001 passou

**Passos:**
1. Localizar o exemplo YAML sob "Campo: pipe.agent.sleeptime"
2. Verificar se a estrutura segue o padrão dos campos anteriores
3. Validar que comentário explicativo está presente

**Resultado esperado:**
- Exemplo YAML mantém formato: `sleeptime: <valor>  # <comentário>`
- Comentário segue padrão dos outros campos (ex: "30 minutos")
- Indentação e formatação idênticas aos campos adjacentes

---

## CT-003 — Seção de impacto coerente com nova descrição

**Tipo:** validação manual

**Critério de aceitação:** Sem quebra de outros campos ou exemplos

**Pré-condição:**
- Arquivo `docs/pipe-yml-config/02-configuracao-global.md` aberto
- CT-001 passou

**Passos:**
1. Localizar a seção "Impacto" sob "Campo: pipe.agent.sleeptime"
2. Verificar se o texto de impacto faz sentido com a nova descrição
3. Validar que não há contradição entre descrição e impacto

**Resultado esperado:**
- Texto de impacto é pertinente à nova descrição (comportamento quando não há trabalho)
- Não há inconsistências semânticas
- Exemplo de valores (1800 = 30 minutos) permanece correto

---

## CT-004 — Campos adjacentes não foram alterados

**Tipo:** validação manual

**Critério de aceitação:** Sem quebra de outros campos ou exemplos

**Pré-condição:**
- Arquivo `docs/pipe-yml-config/02-configuracao-global.md` aberto
- Commit da correção realizado

**Passos:**
1. Verificar campo `pipe.agent.timeout` está íntegro
2. Verificar campo `ttl-log` está íntegro
3. Verificar campo `doc` está íntegro
4. Verificar exemplo completo YAML está integro

**Resultado esperado:**
- Nenhum campo adjacente foi removido ou modificado
- Exemplo completo no final do arquivo contém todos os 4 campos
- Estrutura geral do arquivo permanece intacta

---

## CT-005 — Descrição anterior não aparece no arquivo

**Tipo:** validação manual

**Critério de aceitação:** Descrição atualizada

**Pré-condição:**
- Arquivo `docs/pipe-yml-config/02-configuracao-global.md` aberto

**Passos:**
1. Usar busca (Ctrl+F) pelo texto: "entre cada ciclo"
2. Verificar se alguma ocorrência retorna

**Resultado esperado:**
- Nenhuma ocorrência de "entre cada ciclo" no arquivo
- Descrição antiga foi completamente substituída
