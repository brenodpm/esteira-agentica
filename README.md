# Esteira Agêntica

Esteira automatizada de agentes de IA com arquitetura hexagonal.

## Requisitos

- Python 3.12+
- Git
- GitHub CLI (`gh`) autenticado
- Chave SSH configurada no GitHub

## Instalação

```bash
pip install pyyaml
```

## Configuração

### 1. Variável de ambiente SSH

```bash
export PIPE_SSH_KEY_FILE=~/.ssh/id_ed25519
```

### 2. Arquivo pipe.yml

```yaml
git:
  repo:
    main: git@github.com:user/repo.git
  flow:
    base: main
    feature:
      prefix: feature/
      create: main
      merge: main

agents:
  kiro-cli:
    dev:
      name: engineering
      model: claude-sonnet-4-20250514

boards:
  platform: github
  backlog:
    name: Backlog
    priority: 0
    flow: feature
    columns:
      todo:
        name: To Do
      doing:
        name: Doing
        agent: dev
        prompt: Execute a tarefa
        change:
          advance: done
      done:
        name: Done
        archive: true
```

## Uso

```bash
python -m src
```

## Estrutura

```
src/
├── core/                   # Domínio
│   ├── log.py              # Logging dual (terminal + arquivo)
│   ├── config.py           # Validação do pipe.yml
│   └── board.py            # Board core + interface BoardPort
├── adapters/               # Implementações
│   └── github_board.py     # Adapter para GitHub Projects V2
└── __main__.py             # Entrada principal

repo/                       # Repositórios clonados
logs/                       # Logs diários
pipe.yml                    # Configuração
```

## Arquitetura Hexagonal

O projeto usa arquitetura hexagonal (ports and adapters) para desacoplar a lógica de negócio das implementações específicas de plataforma.

```
┌─────────────────────────────────────────┐
│              __main__.py                │
│         (orquestração)                  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│                core/                    │
│  ┌─────────┐ ┌────────┐ ┌───────────┐  │
│  │  log    │ │ config │ │   board   │  │
│  └─────────┘ └────────┘ └─────┬─────┘  │
│                               │        │
│                         BoardPort      │
└───────────────────────────────┼────────┘
                                │
┌───────────────────────────────▼────────┐
│              adapters/                 │
│  ┌─────────────────────────────────┐   │
│  │       github_board.py           │   │
│  │   (GitHub Projects V2)          │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │       clickup_board.py (TODO)   │   │
│  └─────────────────────────────────┘   │
└────────────────────────────────────────┘
```

## Rate Limit (GitHub)

O adapter do GitHub implementa controle automático de rate limit:

### Throttle
- Sleep antes de cada chamada (inicia em 16s)
- Dobra ao receber secondary rate limit (até 64s)
- Regride após 1h sem problemas

### Penalty
- Ativado quando throttle atinge 64s e ainda falha
- Bloqueia chamadas por N horas (dobra a cada ativação)
- Regride após 1h sem problemas

### Logs
```
[GitHub] [16s] brenodpm - Resolvendo owner
[GitHub] [16s] brenodpm - Listando projects
[GitHub] [32s] Secondary rate limit - aguardando 60s
```

## Documentação Técnica

Ver [CONTEXT.md](CONTEXT.md) para decisões técnicas e estado do projeto.
