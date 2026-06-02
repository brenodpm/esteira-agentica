Status: approved
Owner: architecture-agent
Last updated: 2026-05-28

## Inputs
- docs/agents/context.md
- docs/agents/*.md
- docs/02-architecture/overview.md
- docs/06-decisions-log/debito-architecture-contrato-artefatos.md

## Descrição

Mapa autoritativo de artefatos da esteira. Define para cada agente: onde lê, onde escreve, nomes de arquivo esperados e campos obrigatórios. É a fonte de verdade para validação automática de pré e pós-condições pelo orquestrador.

---

## Mapa por agente

### product-agent

| Tipo | Path | Campos obrigatórios |
|------|------|---------------------|
| **Input** | `docs/00-product/` (leitura livre) | — |
| **Output: vision.md** | `docs/00-product/vision.md` | Status, Owner, Last updated, problema, solução, público-alvo, proposta de valor |
| **Output: problem-space.md** | `docs/00-product/problem-space.md` | Status, Owner, Last updated, contexto, problemas, impacto, oportunidade |
| **Output: epicos.md** | `docs/00-product/epicos.md` | Status, Owner, Last updated, ≥1 épico com objetivo + escopo + fora de escopo |

---

### requirements-agent

| Tipo | Path | Campos obrigatórios |
|------|------|---------------------|
| **Input** | `docs/00-product/vision.md` | Status: approved |
| **Input** | `docs/00-product/problem-space.md` | Status: approved |
| **Input** | `docs/00-product/epicos.md` | Status: approved |
| **Output: user stories** | `docs/01-requirements/user-stories/us-<id>-<slug>.md` | Status, Owner, Last updated, Como/Quero/Para, Critérios de aceitação (Dado/Quando/Então) |
| **Output: regras de negócio** | `docs/01-requirements/business-rules.md` | Status, Owner, Last updated, ≥1 RN com descrição + contexto + exceções |

---

### architecture-agent

| Tipo | Path | Campos obrigatórios |
|------|------|---------------------|
| **Input** | `docs/01-requirements/user-stories/*.md` | Status: approved |
| **Input** | `docs/01-requirements/business-rules.md` | Status: approved |
| **Input (opcional)** | `docs/00-product/*.md` | — |
| **Input (opcional)** | `docs/06-decisions-log/*.md` | — |
| **Output: overview.md** | `docs/02-architecture/overview.md` | Status, Owner, Last updated, Visão geral, Estilo arquitetural, Componentes (tabela), Fluxo principal |
| **Output: constraints.md** | `docs/02-architecture/constraints.md` | Status, Owner, Last updated, Restrições técnicas, Premissas, Requisitos não funcionais (tabela) |
| **Output: ADRs** | `docs/02-architecture/adr-<NNN>-<slug>.md` | Status, Owner, Last updated, Contexto, Decisão, Justificativa, Consequências |
| **Output: componentes** | `docs/02-architecture/cmp-<slug>.md` | Status, Owner, Last updated, Responsabilidade, Entradas, Saídas, Dependências |
| **Output: artifact-map.md** | `docs/02-architecture/artifact-map.md` | Este arquivo |

---

### tech-lead-agent

| Tipo | Path | Campos obrigatórios |
|------|------|---------------------|
| **Input** | `docs/02-architecture/overview.md` | Status: approved |
| **Input** | `docs/02-architecture/constraints.md` | Status: approved |
| **Input** | `docs/01-requirements/user-stories/*.md` | Status: approved |
| **Output: tasks** | `docs/04-tasks/task<NN>-<slug>.md` | Status, Owner, Last updated, Descrição, User story relacionada, Escopo técnico, Fora de escopo, Critério de aceite, Dependências |

---

### engineering-agent

| Tipo | Path | Campos obrigatórios |
|------|------|---------------------|
| **Input** | `docs/04-tasks/task<NN>-<slug>.md` | Status: ready |
| **Input** | `docs/02-architecture/overview.md` | Status: approved |
| **Input** | `docs/03-technical-design/` (se existir) | — |
| **Output: código** | `src/` (conforme arquitetura) | Testes unitários incluídos |
| **Output: design técnico** | `docs/03-technical-design/td-<slug>.md` | Status, Owner, Last updated, Decisões de implementação, Changes |

---

### quality-agent

| Tipo | Path | Campos obrigatórios |
|------|------|---------------------|
| **Input** | `docs/01-requirements/user-stories/*.md` | Status: approved |
| **Input** | `docs/04-tasks/task<NN>-<slug>.md` | Status: done |
| **Input** | `src/` (código implementado) | — |
| **Output: casos de teste** | `docs/05-tests/tc-<slug>.md` | Status, Owner, Last updated, CT-id, User story, Pré-condição, Passos, Resultado esperado, Status (pass/fail/blocked) |
| **Output: resultados** | `docs/05-tests/results/tr-<slug>.md` | Status, Owner, Last updated, resumo de execução, lista de CTs com resultado |
| **Output: bugs** | `docs/05-tests/results/bug-<slug>.md` | Severidade, Status, Last updated, Descrição, Reprodução, Esperado, Obtido |

---

## Regras de validação do orquestrador

1. **Pré-condição de etapa**: todos os inputs listados devem existir com `Status: approved`
2. **Pós-condição de etapa**: todos os outputs obrigatórios devem existir com `Status: draft` ou superior
3. **Gate de aprovação**: o orquestrador aguarda `Status: approved` nos outputs antes de avançar
4. **Débito automático**: se um artefato esperado não existe, criar débito em `docs/06-decisions-log/debito-<agente>-artefato-ausente.md`

---

## Convenções de nomenclatura

| Padrão | Exemplo |
|--------|---------|
| `us-<id>-<slug>.md` | `us-001-autenticacao-usuario.md` |
| `adr-<NNN>-<slug>.md` | `adr-007-kiro-como-runtime.md` |
| `cmp-<slug>.md` | `cmp-orchestrator.md` |
| `task<NN>-<slug>.md` | `task12-artifact-validation.md` |
| `tc-<slug>.md` | `tc-task12-artifact-validation.md` |
| `tr-<slug>.md` | `tr-task12-artifact-validation.md` |
| `bug-<slug>.md` | `bug-task12-ct001-path-incorreto.md` |
| `td-<slug>.md` | `td-orchestrator-validation.md` |
| `debito-<agente>-<titulo>.md` | `debito-architecture-contrato-artefatos.md` |
