Status: approved
Owner: architecture-agent
Last updated: 2026-05-26

## Inputs
- docs/02-architecture/overview.md
- docs/01-requirements/meeting-01.md
- docs/gitflow.md

## Responsabilidade

Abstrai operações de versionamento local. Cria branches seguindo o gitflow configurado, executa commits com mensagens padronizadas e prepara o repositório para abertura de PR (via `integrations/github`).

## Entradas

- Configuração de gitflow do projeto via `config/` (branch base, prefixos, convenção de commit)
- Comando de ação (criar branch, commit, push) via `orchestrator`
- Dados do commit (mensagem, arquivos) via `orchestrator`

## Saídas

- Branch criada e publicada no remote
- Commit realizado com mensagem padronizada
- Confirmação de push para abertura de PR

## Dependências

- `git` CLI disponível e configurado localmente
- `config` — leitura do gitflow configurado por projeto
- Sem dependência de outros módulos internos
