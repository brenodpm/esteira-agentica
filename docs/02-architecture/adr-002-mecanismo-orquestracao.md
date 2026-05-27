Status: accepted
Owner: architecture-agent
Last updated: 2026-05-26

## Inputs
- docs/00-product/epicos.md
- docs/01-requirements/meeting-01.md
- docs/02-architecture/constraints.md
- docs/02-architecture/overview.md

## Contexto

O sistema precisa sequenciar agentes de IA em ordem definida, pausar para aprovação humana entre etapas, retomar de onde parou em caso de falha ou rejeição, e fazer tudo isso sem UI própria — toda interação ocorre via GitHub.

As opções consideradas foram:

1. **Loop imperativo com estado em arquivo** — orquestrador Python com máquina de estados simples persistida em JSON/SQLite
2. **Framework de workflow** (Prefect, Airflow, Temporal) — engine externa com scheduler e UI
3. **GitHub Actions** — pipeline CI/CD como orquestrador

## Decisão

**Loop imperativo com máquina de estados persistida localmente** (opção 1).

O orquestrador é um script Python que:
- Lê o estado atual da execução (etapa corrente, feature em andamento, resultado do último agente)
- Executa o próximo agente via `subprocess` (Kiro CLI)
- Persiste o resultado e avança o estado
- Posta o resultado na issue do GitHub e aguarda label de aprovação antes de avançar
- Retoma do estado persistido em caso de interrupção

## Justificativa

- Frameworks externos (opção 2) violam a restrição de ferramentas gratuitas ou adicionam dependências pesadas sem benefício para execução single-machine
- GitHub Actions (opção 3) exige push para cada etapa, adiciona latência e não permite execução local offline
- Loop imperativo é suficiente para o volume e a complexidade do sistema: execução sequencial, single-machine, sem paralelismo entre agentes
- Estado em arquivo é auditável, versionável e recuperável sem infraestrutura adicional
- Alinha com a decisão de Python stdlib-only (ADR-001)

## Consequências

- Positivas: zero dependências externas; estado auditável; fácil de debugar; retomada trivial
- Negativas: sem UI de monitoramento nativa (mitigado pelo GitHub como interface); sem paralelismo (não é requisito)
- Riscos: processo Python pode ser interrompido pelo SO — mitigado por persistência de estado a cada transição
