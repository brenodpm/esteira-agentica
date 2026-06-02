# Esteira Agêntica

Orquestração automática de agentes de IA integrada ao GitHub e ao git local.

## O que é

Uma esteira de desenvolvimento que elimina o humano como orquestrador. Agentes de IA especializados (product, requirements, architecture, tech-lead, engineering, quality) são acionados automaticamente conforme o backlog do GitHub, produzem artefatos rastreáveis e aguardam aprovação humana nos gates entre etapas.

**Prioridade central:** minimizar consumo de tokens — cada agente lê apenas o necessário, evita reprocessamento e produz saídas enxutas.

## Pré-requisitos

| Ferramenta | Versão | Instalação |
|------------|--------|------------|
| Git | 2.x+ | https://git-scm.com |
| GitHub CLI | 2.x+ | https://cli.github.com |
| Kiro CLI | latest | https://kiro.dev |
| Python | 3.11+ | https://python.org |
| PyYAML | 6.x+ | `pip install pyyaml` |

Conta GitHub com repositório criado e token com escopos `repo`, `project`, `read:org`.

## Início rápido

### 1. Clonar e instalar

```bash
git clone https://github.com/brenodpm/esteira-agentica
cd esteira-agentica
pip install pyyaml
```

### 2. Configurar o projeto

Crie `esteira.yml` na raiz do seu projeto:

```yaml
doc: docs/
git:
  repo: "seu-usuario/seu-repositorio"
boards:
  task:
    name: Tarefas
    todo: backlog
    columns:
      backlog:
        name: Backlog
        change:
          executar: em-progresso
          cancelar: cancelado
      em-progresso:
        name: Em Progresso
        agent: engineering
        acao: "Implementar a tarefa"
        change:
          concluir: concluido
      concluido:
        name: Concluído
      cancelado:
        name: Cancelado
```

Ver `esteira.yml` neste repositório como exemplo completo com gitflow e múltiplos boards.

### 3. Copiar os agentes Kiro

```bash
cp -r .kiro/ /seu-projeto/.kiro/
```

Os agentes são genéricos — funcionam em qualquer projeto, independente de linguagem ou estrutura.

### 4. Autenticar e usar

```bash
kiro auth
gh auth login
```

Abra o Kiro CLI no seu projeto e acione o agente desejado (ex: `product` para iniciar pelo produto).

## Fluxo da esteira

```
esteira.yml (config)
       │
       ▼
GitHub Issues (backlog)
       │
       ▼
  orchestrator
       │
       ├─► product → requirements → architecture → tech-lead → engineering → quality
       │
       ├─► gate de aprovação humana entre etapas
       │
       └─► métricas de tokens e tempo por agente
```

## Agentes disponíveis

| Agente | Papel | Atalho |
|--------|-------|--------|
| `product` | Visão, épicos, problem-space | Ctrl+Shift+1 |
| `requirements` | User stories, regras de negócio | Ctrl+Shift+2 |
| `architecture` | Estrutura técnica, ADRs | Ctrl+Shift+3 |
| `tech-lead` | Decomposição em tarefas | Ctrl+Shift+4 |
| `engineering` | Implementação com TDD | Ctrl+Shift+5 |
| `quality` | Casos de teste, bugs | Ctrl+Shift+6 |

## Estrutura de artefatos

```
docs/
├── 00-product/       # vision, problem-space, epicos, migration-plan
├── 01-requirements/  # user stories, regras de negócio
├── 02-architecture/  # overview, ADRs, constraints, artifact-map
├── 03-technical-design/
├── 04-tasks/         # tarefas decompostas pelo tech-lead
├── 05-tests/         # casos de teste e resultados
├── 06-decisions-log/ # débitos e decisões
└── 07-glossary/
```

## Adoção em projeto existente

Ver [docs/00-product/migration-plan.md](docs/00-product/migration-plan.md) para o guia completo de adoção incremental, incluindo diagnóstico do estado atual, checklist de pré-requisitos e variações de contexto.

## Contribuindo

Este projeto é desenvolvido usando a própria esteira. Para contribuir:

1. Abra uma issue no board descrevendo a melhoria
2. A esteira processa a issue pelos agentes em sequência
3. Aprovação humana em cada gate antes de avançar

## Licença

MIT
