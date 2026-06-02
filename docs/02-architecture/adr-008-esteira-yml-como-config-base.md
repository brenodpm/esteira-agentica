Status: approved
Owner: architecture-agent
Last updated: 2026-05-31

## Inputs
- docs/02-architecture/overview.md
- docs/00-product/migration-plan.md
- src/config/loader.py
- config/project.json (substituído)

## Contexto

O projeto usava `config/project.json` como fonte de configuração. O arquivo tinha estrutura flat (repo, gitflow, board, agents_sequence) e não cobria os boards com suas colunas, agentes e transições — informações essenciais para o orquestrador operar.

Paralelamente, o arquivo `esteira.yml` foi criado como schema de configuração completo da esteira, cobrindo:
- Configuração do repositório e gitflow
- Boards com colunas, agentes, ações e transições de estado
- Configurações de execução do pipeline (timeout, sleeptime)

## Decisão

**`esteira.yml` na raiz do projeto é a única fonte de verdade para configuração da esteira.**

`config/project.json` é descontinuado. O loader (`src/config/loader.py`) passa a ler exclusivamente `esteira.yml`.

## Justificativa

1. **Completude**: `esteira.yml` cobre boards com colunas e transições — informação que `project.json` não tinha e que o orquestrador precisa para operar
2. **Formato**: YAML é mais legível para configurações hierárquicas com múltiplos níveis (boards → colunas → agentes → transições)
3. **Convenção**: arquivos de configuração de ferramentas de desenvolvimento tipicamente ficam na raiz do projeto (`.github/`, `pyproject.toml`, `docker-compose.yml`)
4. **Adoção**: um único arquivo na raiz é mais fácil de encontrar e configurar para novos usuários da esteira
5. **Extensibilidade**: o schema YAML permite adicionar novos campos sem quebrar compatibilidade

## Campos obrigatórios

```yaml
doc: <diretório-base-docs>
git:
  repo: <owner/repo>
boards:
  <id>:
    name: <nome>
    todo: <coluna-inicial>
    columns:
      <id>:
        name: <nome>
```

## Campos opcionais com defaults

| Campo | Default | Descrição |
|---|---|---|
| `git.flow.base` | `main` | Branch base do gitflow |
| `pipe.agent.timeout` | `null` | Timeout por agente (minutos) |
| `pipe.agent.sleeptime` | `null` | Dormência sem tasks (minutos) |

## Consequências

- `config/project.json` mantido no repositório por compatibilidade histórica, mas não é mais lido pelo sistema
- Todos os agentes Kiro devem incluir `esteira.yml` em `contextFiles` para ter acesso à configuração
- O migration-plan.md deve orientar novos usuários a criar `esteira.yml` (não `project.json`)
- Testes de config reescritos para o novo formato YAML

## Alternativas consideradas

**Manter `project.json` e adicionar campos de board**: descartado — misturaria dois formatos e não resolveria a legibilidade de configurações hierárquicas.

**Usar variáveis de ambiente**: descartado — não é versionável nem auditável, contradiz os princípios do projeto.
