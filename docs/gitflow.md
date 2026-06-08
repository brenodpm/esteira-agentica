# Gitflow da Esteira

Status: approved
Owner: engineering-agent
Last updated: 2026-06-08

## Inputs
- esteira.yml (seção git.flow)
- src/integrations/git/client.py

---

## Visão Geral

A esteira gerencia branches automaticamente com base na configuração `git.flow` do `esteira.yml`. O ciclo completo de uma etapa com git é:

1. Identificar a branch base (fixa ou dinâmica)
2. Fazer fetch + pull da branch base
3. Criar branch de trabalho
4. Executar o agente, commitar e fazer push
5. Abrir PR para a branch de merge correta
6. Cleanup: voltar para branch principal e apagar branches locais

---

## Configuração (esteira.yml)

```yaml
git:
  repo: "org/repo"
  flow:
    base: main          # branch principal do repositório
    cleanup: true       # limpa branches locais após cada etapa

    feature:
      prefix: feature
      create: main      # branch base para criação (fixa)
      merge: release    # branch alvo do PR (prefixo → dinâmica)

    release:
      prefix: release
      create: main
      merge: main

    hotfix:
      prefix: hotfix
      create: main
      merge: main

    bugfix:
      prefix: fix
      create: release   # prefixo → dinâmica
      merge: release    # prefixo → dinâmica
```

### Campos

| Campo | Descrição |
|-------|-----------|
| `base` | Branch principal do repositório. Usada como fallback e destino do cleanup. |
| `cleanup` | Se `true`, após cada etapa a esteira faz checkout para `base` e apaga todas as branches locais. |
| `prefix` | Prefixo usado para nomear branches de trabalho (ex: `feature/minha-task`). |
| `create` | Branch base para criação da branch de trabalho. |
| `merge` | Branch alvo onde o PR será aberto. |

---

## Resolução de Branch: Fixa vs Dinâmica

### Branch Fixa

Quando `create` ou `merge` aponta para uma branch que **não é prefixo de nenhum flow** (ex: `main`, `develop`):

- A esteira faz `git fetch origin <branch>` + `git checkout <branch>` + `git pull`
- Usa essa branch diretamente como base ou alvo

### Branch Dinâmica (Prefixo)

Quando `create` ou `merge` é igual ao `prefix` de outro flow (ex: `release`, `feature`):

- A esteira **não sabe qual branch exata usar** (pode ser `release/v1.0`, `release/v2.0`, etc.)
- A branch exata deve ser informada **na issue** via um dos mecanismos abaixo

---

## Como Informar a Branch Dinâmica na Issue

### Opção 1: Label

Adicionar uma label no formato:

```
branch:<nome-completo-da-branch>
```

Exemplo: `branch:release/v1.0`

### Opção 2: Marcador no Body

Incluir no corpo da issue um comentário HTML:

```html
<!-- branch: release/v1.0 -->
```

Isso permite que a informação fique invisível na renderização mas legível pela esteira.

### Prioridade de Resolução

1. Label `branch:<nome>` (verificada primeiro)
2. Marcador `<!-- branch: <nome> -->` no body
3. Se nenhum for encontrado → a esteira **bloqueia a issue** automaticamente:
   - Posta um comentário explicando como adicionar a label
   - Adiciona a label `blocked`
   - Para a execução da issue
   - Para retomar: adicione a label `branch:<nome>` e remova `blocked`

---

## Ciclo de Vida Completo

### 1. Identificação da Branch Base

```
flow_key = board.flow  (ex: "feature")
create_ref = git.flow[flow_key].create  (ex: "main" ou "release")

Se create_ref é branch fixa → usa direto
Se create_ref é prefixo → resolve via issue (label ou body)
```

### 2. Fetch + Checkout da Base

```bash
git fetch origin <branch-base>
git checkout <branch-base>
git pull origin <branch-base>
```

### 3. Criação da Branch de Trabalho

```bash
git checkout -b <prefix>/<slug-do-titulo>
# Ex: feature/implementar-login
```

### 4. Commit + Push

Após o agente executar:

```bash
git add -A
git commit -m "[#<issue>] <role>: <titulo>"
git push -u origin <branch-de-trabalho>
```

### 5. Abertura do PR

```
merge_ref = git.flow[flow_key].merge  (ex: "main" ou "release")

Se merge_ref é branch fixa → PR aponta para ela
Se merge_ref é prefixo → resolve via issue (mesma lógica do create)
```

### 6. Cleanup

Se `git.flow.cleanup: true`:

```bash
git checkout <base>          # ex: main
git pull origin <base>
git branch -D <todas-as-branches-exceto-base>
```

---

## Exemplos Práticos

### Feature criada a partir de main, PR para release/v1.0

```yaml
# esteira.yml
feature:
  prefix: feature
  create: main       # fixa
  merge: release     # dinâmica
```

Issue deve ter: `branch:release/v1.0`

Resultado:
- Checkout `main`, pull
- Cria `feature/minha-feature`
- PR aberto contra `release/v1.0`

### Bugfix criada a partir de release/v1.0, PR para release/v1.0

```yaml
bugfix:
  prefix: fix
  create: release    # dinâmica
  merge: release     # dinâmica
```

Issue deve ter: `branch:release/v1.0`

Resultado:
- Checkout `release/v1.0`, pull
- Cria `fix/corrigir-bug`
- PR aberto contra `release/v1.0`

### Hotfix a partir de main, PR para main

```yaml
hotfix:
  prefix: hotfix
  create: main       # fixa
  merge: main        # fixa
```

Nenhuma label necessária.

Resultado:
- Checkout `main`, pull
- Cria `hotfix/fix-critico`
- PR aberto contra `main`

---

## Vinculação Board → Flow

Cada board no `esteira.yml` declara qual flow utiliza:

```yaml
boards:
  task:
    flow: feature    # usa git.flow.feature
  bug:
    flow: bugfix     # usa git.flow.bugfix
  demanda:
    flow: doc        # usa git.flow.doc
```

---

## Changes
- Reescrita completa da documentação de gitflow
- Documentação da resolução de branch fixa vs dinâmica
- Documentação do mecanismo de label/body para branches dinâmicas
- Documentação do cleanup pós-etapa
