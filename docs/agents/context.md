# CONTEXT.md

## 📌 Definição

Esteira de desenvolvimento multi-agentes de IA com execução manual.

---

## ⚙️ Core Rules (Obrigatório)

* Não assumir contexto implícito
* Não misturar níveis (negócio vs técnico)
* Respeitar o escopo do agente
* Justificar decisões relevantes (somente quando houver decisão)
* Utilizar padrões consolidados do mercado
* Evitar ambiguidade (clareza > verbosidade)
* Tudo deve ser versionável, rastreável e auditável
* É PROIBIDO continuar execução com inconsistências entre documentos
* Divergências entre artefatos devem gerar débito obrigatório
* Atualizar status das tarefas
* **Não prometer o que não se sabe se pode ser cumprido**
* **Ideias cuja viabilidade é incerta devem ser explicitamente marcadas como incerteza e sinalizadas para amadurecimento futuro — nunca tratadas como decisão**

---

## 🚫 Restrições

* Não atuar fora do seu papel
* Não modificar arquivos fora da sua área
* Não gerar conteúdo genérico sem contexto
* Não sobrescrever conteúdo sem justificativa
* Não repetir informação já existente sem necessidade

---

## 🚧 Definition of Ready (Gate entre etapas)

Um agente só pode iniciar sua execução se TODOS os critérios abaixo forem atendidos:

- Artefatos obrigatórios da etapa anterior existem
- Artefatos estão com Status: approved
- Não existem débitos abertos que impactem a etapa
- Inputs estão explicitamente listados

Caso não atenda:
→ Criar débito
→ Parar execução

---

## 📄 Padrão de Documento (Obrigatório)

```md id="docpadrao"
Status: draft | approved | deprecated
Owner: <agent-name>
Last updated: YYYY-MM-DD

## Inputs
- caminho/arquivo.md
```

---

## 🔄 Execução (Simplificada)

1. Ler input do usuário
2. Ler apenas os artefatos necessários
3. Identificar lacunas ou inconsistências

### Se houver bloqueio:

* Criar débito em:

  ```
  docs/06-decisions-log/debito-<agent>-<titulo>.md
  ```
* Parar execução e solicitar ação do usuário

### Se NÃO houver bloqueio:

4. Evoluir ou criar artefatos

---

## ❓ Missing Inputs

Se faltar informação:

* Máximo 5 perguntas
* Apenas perguntas bloqueadoras
* Não repetir perguntas já feitas

---

## Template de Débito

Status: open | resolved
Owner: <agent>
Last updated: YYYY-MM-DD

* Descrição
* Impacto
* Responsável pela resolução
* Bloqueia etapa? (sim/não)

---

## 🧾 Controle de Mudanças (Obrigatório)

Para alterações em arquivos existentes:

```md id="changes"
## Changes
- <o que foi alterado>
- <motivo>
```

---

## 🧠 Planejamento (Leve)

Antes de executar:

* Dividir em pequenas etapas
* Evitar respostas longas desnecessárias
* Priorizar menor consumo de tokens

---

## 📁 Estrutura de Diretórios

```md id="dirs"
docs/
├── 00-product/
├── 01-requirements/
├── 02-architecture/
├── 03-technical-design/
├── 04-quality/
├── 05-operations/
├── 06-decisions-log/
└── 07-glossary/
```

---

## 🔗 Fluxo entre agentes

Product → Requirements → UX → Architecture → Engineering → Quality → Ops

---

## 📦 Responsabilidade por Etapa

| Etapa            | Saída                |
| ---------------- | -------------------- |
| Product          | Visão, épicos        |
| Requirements     | User stories, regras |
| Architecture     | Estrutura e decisões |
| Technical Design | Especificação        |
| Quality          | Testes               |
| Operations       | Execução             |

---

## ✅ Definition of Done (Simplificado)

Uma etapa termina quando:

* Artefatos obrigatórios existem
* Não há dúvidas críticas abertas
* Próximo agente consegue atuar sem suposições

---

## 📌 Diretrizes Gerais

* Preferir precisão a completude
* Evoluir incrementalmente
* Evitar reprocessamento
* Minimizar consumo de tokens


## Changes
- Adicionadas duas core rules sobre honestidade e incerteza
- Motivo: diretriz global definida pelo usuário para todos os agentes