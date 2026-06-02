Status: approved
Owner: product-agent
Last updated: 2026-06-02

## Issue
#15 — Criar um manual do usuário para o projeto

## Inputs
- docs/00-product/issue-15-vision.md
- docs/00-product/issue-15-problem-space.md
- docs/00-product/migration-plan.md
- docs/00-product/epicos.md

---

## Épico: Distribuição dos Artefatos da Esteira

**Objetivo:** Permitir que o usuário obtenha os arquivos necessários para rodar a esteira sem clonar o repositório completo.

**Escopo:**
- Definir quais arquivos são necessários para rodar: `esteira.yml` (template), `.kiro/agents/`, `docs/agents/`, `src/`
- Criar mecanismo de distribuição: release no GitHub com arquivo `.zip` ou instruções de download seletivo via `gh` ou `curl`
- Garantir que o conjunto de arquivos seja autocontido e versionado

**Fora de escopo:** Publicação em PyPI, Docker, homebrew ou qualquer package manager.

---

## Épico: Manual do Usuário

**Objetivo:** Guiar qualquer desenvolvedor do zero até a esteira rodando, sem suporte humano e sem clonar o repositório.

**Escopo:**
- Documento `docs/manual-usuario.md` com:
  - O que é a esteira (2–3 linhas)
  - Pré-requisitos: Git, GitHub CLI, Kiro CLI, Python 3.11+, PyYAML
  - Como obter os arquivos (download da release, sem clone)
  - Como configurar `esteira.yml` para o projeto do usuário
  - Como configurar os agentes Kiro (`.kiro/agents/`)
  - Como autenticar: `gh auth login`, `kiro auth`
  - Como executar: `python -m src`
  - Como usar o comando `python -m src sync`
  - Checklist de verificação antes de executar
- O documento deve ser executável: cada passo tem o comando exato, sem ambiguidade

**Fora de escopo:** Tutorial em vídeo, tradução, documentação de API, guia de contribuição.

---

## Épico: Atualização do README

**Objetivo:** Tornar o README o ponto de entrada público que direciona o usuário ao manual.

**Escopo:**
- Seção "Como usar" no README apontando para `docs/manual-usuario.md`
- Descrição de uma linha do que é a esteira
- Badge de versão ou status (opcional)

**Fora de escopo:** Reescrita completa do README, seção de contribuição, changelog.
