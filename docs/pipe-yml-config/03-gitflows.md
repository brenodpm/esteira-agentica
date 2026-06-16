# Configuração de Git Flows

Os gitflows definem como branches são criadas, nomeadas e mescladas durante o ciclo de vida de uma issue.

## Estrutura Base

```yaml
git:
  repo: "owner/repo"           # Identificador do repositório GitHub
  flow:
    base: main                 # Branch base do projeto
    cleanup: true              # Remove branches locais após cada operação
```

## Definindo um Gitflow

Cada gitflow é um tipo de branch com seu próprio ciclo de vida:

```yaml
feature:
  prefix: feature              # Prefixo das branches criadas (feature/task-123)
  description: "..."           # Descrição legível do propósito
  create: main                 # De onde a branch será criada (branch fixa ou prefixo)
  merge: epic                  # Para onde o merge será direcionado (branch fixa ou prefixo)
```

### Tipos de Origem/Destino

- **Branch fixa** (ex: `main`, `develop`) — sempre usa essa branch
- **Prefixo de outro flow** (ex: `epic`, `release`) — resolve via label/tag na issue

## Resolvendo Prefixos Dinâmicos

Quando uma issue usa um gitflow com `create` ou `merge` que aponta para um prefixo:

```yaml
epic:
  prefix: epic
  create: main        # Sempre cria da main
  merge: release      # merge → para qual branch release? (v1.0? v2.0?)
```

A esteira busca a branch específica via:

1. Label `/branch <nome>` na issue (ex: `/branch release/v1.0`)
2. Comentário no body: `<!-- branch: release/v1.0 -->`

## Exemplo: Setup Completo

```yaml
git:
  repo: "brenodpm/esteira-agentica"
  flow:
    base: main
    cleanup: true

    hotfix:
      prefix: hotfix
      description: "Correção de bugs em produção"
      create: main
      merge: main

    release:
      prefix: release
      description: "Branch de release"
      create: main
      merge: main

    epic:
      prefix: epic
      description: "Branch para épicos — planejamento e documentação"
      create: main
      merge: release  # Prefixo → resolver via issue

    feature:
      prefix: feature
      description: "Branch de feature"
      create: epic    # Prefixo → resolver via issue
      merge: epic

    bugfix:
      prefix: fix
      description: "Correção de bugs em homologação"
      create: epic    # Prefixo → resolver via issue
      merge: epic
```

## Impacto das Configurações

- **prefix**: Define o padrão de nomenclatura automática de branches
- **create**: Determina de onde a branch é derivada (importante para organização hierárquica)
- **merge**: Controla para onde os PRs serão abertos
- **cleanup: true**: Mantém workspace limpo, removendo branches locais após uso

## Boas Práticas

1. Use prefixos padronizados (feature/, fix/, release/, hotfix/)
2. Organize hierarquicamente: features vêm de epics, epics vêm de main
3. Para workspaces compartilhados, mantenha `cleanup: true`
4. Documente o propósito de cada flow na `description`
