Status: accepted
Owner: architecture-agent
Last updated: 2026-05-26

## Inputs
- docs/01-requirements/meeting-01.md
- docs/02-architecture/constraints.md

## Contexto

A linguagem e o runtime não foram definidos nos requisitos — a decisão foi explicitamente delegada ao arquiteto (meeting-01.md). O sistema precisa:

- Invocar Kiro CLI via subprocesso
- Executar comandos `git` e `gh` via shell
- Ler/escrever arquivos locais (artefatos, estado, métricas)
- Parsear JSON (respostas da GitHub API via `gh`)
- Rodar em Linux sem dependências pagas

## Decisão

**Python 3.11+** como linguagem e runtime principal.

## Justificativa

- Disponível por padrão na maioria das distribuições Linux sem instalação adicional
- Biblioteca padrão cobre todos os casos de uso: `subprocess` (invocar CLI), `pathlib` (arquivos), `json`, `sqlite3` (persistência local)
- Sem necessidade de compilação ou build step — execução direta
- Ecossistema maduro para automação de shell e integração com APIs
- Menor overhead de setup comparado a Node.js (sem `npm install`) ou Go (sem compilação)
- Familiaridade ampla — reduz barreira para manutenção futura

## Consequências

- Positivas: zero dependências externas para o núcleo do sistema; execução imediata; fácil leitura e manutenção
- Negativas: tipagem dinâmica exige disciplina; performance inferior a Go/Rust (irrelevante para este caso de uso)
- Riscos: versão do Python disponível na máquina pode variar — mitigado exigindo 3.11+ e verificando na inicialização
