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

Cada gitflow é um tipo de branch com seu próprio ciclo de vida. A esteira gerencia automaticamente:

- **Criação**: Branch criada no momento da tarefa
- **Nomenclatura**: Seguindo padrão `{prefix}/{issue-id}-{slug}`  
- **Merge**: Pull request aberto para branch de destino
- **Cleanup**: Remoção automática após conclusão

```yaml
feature:
  prefix: feature              # Prefixo das branches criadas (feature/task-123)
  description: "..."           # Descrição legível do propósito
  create: main                 # De onde a branch será criada (branch fixa ou prefixo)
  merge: epic                  # Para onde o merge será direcionado (branch fixa ou prefixo)
```

### Anatomia de um Gitflow

- **prefix**: Define padrão de nomenclatura. Usado em `{prefix}/{id}-{slug}`
- **description**: Documentação interna - aparece em logs e relatórios da esteira
- **create**: Branch origem - onde `git checkout -b` será executado
- **merge**: Branch destino - onde o pull request será aberto

### Tipos de Origem/Destino

- **Branch fixa** (ex: `main`, `develop`) — sempre usa essa branch específica
- **Prefixo de outro flow** (ex: `epic`, `release`) — resolve dinamicamente via labels da issue

#### Exemplo Prático: Branch Fixa vs Prefixo

```yaml
# Branch fixa - sempre usa 'main'
hotfix:
  create: main    # ✓ git checkout -b hotfix/bug-123 main
  merge: main     # ✓ Pull request: hotfix/bug-123 → main

# Prefixo dinâmico - resolve via issue
feature:
  create: epic    # ? Qual epic? epic/story-456? epic/milestone-789?
  merge: epic     # Depende da resolução do create
```

## Resolvendo Prefixos Dinâmicos

Quando uma issue usa um gitflow com `create` ou `merge` que aponta para um prefixo, a esteira precisa determinar qual branch específica usar.

### Processo de Resolução

```yaml
epic:
  prefix: epic
  create: main        # ✓ Sempre cria da main (branch fixa)
  merge: release      # ? Para qual release? release/v1.0? release/v2.0?
```

**Passo 1**: A esteira identifica que `merge: release` é um prefixo (não uma branch fixa)

**Passo 2**: Busca resolução na issue, nesta ordem de prioridade:

1. **Label `/branch <nome>`** na issue
   ```
   /branch release/v1.0
   ```

2. **Comentário HTML no body** da issue
   ```markdown
   <!-- branch: release/v1.0 -->
   ```

**Passo 3**: Se encontrado, usa `release/v1.0`. Se não encontrado, falha e reporta erro.

### Casos de Uso Comuns

#### Epic → Release
```yaml
epic:
  merge: release    # Precisa resolver qual release
```

Issue epic com label `/branch release/v2.0` resultará em:
- Pull request: `epic/story-123 → release/v2.0`

#### Feature → Epic  
```yaml
feature:
  create: epic      # Precisa resolver qual epic
  merge: epic       # Mesmo epic (consistência)
```

Issue feature com `<!-- branch: epic/user-management -->` resultará em:
- Criação: `git checkout -b feature/task-456 epic/user-management`
- Pull request: `feature/task-456 → epic/user-management`

### Cenários de Erro

- **Prefixo sem resolução**: Issue usa gitflow com prefixo mas não tem label/comentário
- **Branch inexistente**: Label aponta para branch que não existe no repositório
- **Resolução inconsistente**: `create: epic` e `merge: feature` com resoluções diferentes

## Criando Gitflows Personalizados

A esteira permite definir gitflows customizados para necessidades específicas do projeto.

### Estrutura Mínima

```yaml
meu_flow:
  prefix: custom              # Nome único do prefixo
  description: "Meu flow personalizado"
  create: main                # Branch de origem  
  merge: main                 # Branch de destino
```

### Casos de Uso para Flows Customizados

#### Documentação e Specs
```yaml
docs:
  prefix: docs
  description: "Atualizações de documentação"
  create: main
  merge: main                 # Docs vão direto para main

spec:
  prefix: spec  
  description: "Especificações e design docs"
  create: epic                # Specs vivem no contexto do épico
  merge: epic
```

#### Ambientes e Deploy
```yaml
staging:
  prefix: staging
  description: "Branch de homologação"  
  create: release             # Criada a partir da release
  merge: main                 # Deploy vai para main

qa:
  prefix: qa
  description: "Branch para testes de qualidade"
  create: feature             # QA testa features específicas
  merge: feature              # Volta correções para a feature
```

#### Tipos Especializados de Correção
```yaml
refactor:
  prefix: refactor
  description: "Refatoração sem mudança de comportamento"
  create: main
  merge: main

security:
  prefix: security  
  description: "Correções de segurança"
  create: main
  merge: main                 # Alta prioridade, direto para main

performance:
  prefix: perf
  description: "Otimizações de performance"  
  create: epic                # Context do épico onde performance importa
  merge: epic
```

### Validações e Restrições

A esteira valida gitflows customizados:

- **prefix** deve ser único no arquivo
- **create** e **merge** devem referenciar branches válidas ou prefixos existentes
- **description** é obrigatória para documentação
- Não pode usar prefixos reservados do sistema (system/, pipe/, etc.)

### Exemplo: Workflow Completo com Customizações

```yaml
git:
  repo: "company/product"
  flow:
    base: main
    cleanup: true

    # Flows padrão
    epic:
      prefix: epic
      description: "Planejamento e épicos"
      create: main
      merge: release

    feature:
      prefix: feature  
      description: "Novas funcionalidades"
      create: epic
      merge: epic

    # Flows customizados
    docs:
      prefix: docs
      description: "Atualizações de documentação"
      create: main
      merge: main

    experiment:
      prefix: exp
      description: "Features experimentais"
      create: feature           # Baseada em feature existente
      merge: feature            # Volta para a feature

    migration:
      prefix: migration
      description: "Migrações de dados e schema"  
      create: release           # Sincronizado com release
      merge: release            # Fica na release até deploy
```

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

### Configurações de Repositório

```yaml
git:
  repo: "owner/repo"      # Determina onde PRs serão abertos
  flow:
    base: main            # Branch padrão para operações de limpeza
    cleanup: true         # Gerenciamento automático de branches locais
```

#### `cleanup: true` vs `cleanup: false`

**Com cleanup ativado**:
- Branch local removida após push
- Workspace sempre limpo
- Ideal para CI/CD e ambientes compartilhados
- Não interfere com branches remotas

**Sem cleanup**:  
- Branches locais acumulam no workspace
- Desenvolvedor controla limpeza manual
- Útil para desenvolvimento local com múltiplas branches ativas

### Configurações de Gitflow

#### `prefix`
```yaml
feature:
  prefix: feat    # Resulta em: feat/123-minha-tarefa
  
enhancement:  
  prefix: enhancement    # Resulta em: enhancement/456-nova-feature
```

**Impacto**: Define namespace das branches. Útil para:
- Organização visual no repositório
- Filtros e busca por tipo
- Políticas de branch protection específicas

#### `create` e `merge`

```yaml
# Workflow linear
hotfix:
  create: main
  merge: main         # main → hotfix → main

# Workflow hierárquico  
feature:
  create: epic
  merge: epic         # epic → feature → epic → release
```

**create** determina:
- Ponto de partida do código
- Commit base para diff do PR
- Dependências e conflitos potenciais

**merge** determina:
- Para onde as alterações fluem
- Quem revisa o PR (owners da branch destino)
- Pipeline de integração ativado

### Comportamentos Avançados

#### Gitflows com Referência Cruzada

```yaml
epic:
  create: main
  merge: release

feature:  
  create: epic      # Herda contexto do epic
  merge: epic       # Mantém mudanças no contexto
  
release:
  create: main  
  merge: main       # Finaliza ciclo
```

**Fluxo resultante**:
1. Epic criado da main → epic/planning-123
2. Feature criada do epic → feature/task-456 (baseada em epic/planning-123)  
3. Feature merged no epic → epic/planning-123 recebe mudanças
4. Epic merged na release → release/v1.0 recebe épico completo
5. Release merged na main → main recebe versão

#### Resolução de Conflitos na Hierarquia

Quando `feature` merge em `epic`, e `epic` já avançou:
- A esteira força rebase da feature antes do merge
- Conflitos aparecem durante a execução da task
- Developer pode resolver via interface de comentários da issue

## Boas Práticas

### Nomenclatura e Organização

1. **Use prefixos semânticos padronizados**
   ```yaml
   feature:   # Novas funcionalidades
     prefix: feature
   
   fix:       # Correções de bugs  
     prefix: fix
   
   hotfix:    # Correções críticas em produção
     prefix: hotfix
   
   release:   # Branches de release
     prefix: release
   ```

2. **Organize hierarquicamente por fluxo de trabalho**
   ```yaml
   # Planejamento → Desenvolvimento → Release
   epic:
     create: main      # Épicos começam da main
     merge: release    # Épicos fluem para release
   
   feature:
     create: epic      # Features começam do épico
     merge: epic       # Features voltam para o épico
   
   release:  
     create: main      # Release consolida da main
     merge: main       # Release volta para main
   ```

### Configurações por Ambiente

#### Desenvolvimento Local (workspace individual)
```yaml
git:
  flow:
    cleanup: false    # Mantém branches para experimentação
    
feature:
  create: main        # Simplifica - não depende de épicos
  merge: main         # Direto para main (menos overhead)
```

#### CI/CD e Produção  
```yaml
git:
  flow:
    cleanup: true     # Workspace sempre limpo
    
feature:
  create: epic        # Respeita hierarquia de planejamento  
  merge: epic         # Consolidação controlada
```

### Estratégias de Branching

#### GitFlow Tradicional
```yaml
feature:
  create: develop
  merge: develop
  
release:
  create: develop
  merge: main
  
hotfix:
  create: main
  merge: main
```

#### GitHub Flow Simplificado  
```yaml
feature:
  create: main
  merge: main
  
hotfix:
  create: main  
  merge: main
```

#### Epic-Based Flow (Projetos Grandes)
```yaml
epic:
  create: main
  merge: release
  
feature:
  create: epic
  merge: epic
  
release:
  create: main
  merge: main
```

### Resolução de Problemas Comuns

#### Erro: "Branch não encontrada para prefixo"
- **Causa**: Issue com gitflow dinâmico sem resolução
- **Solução**: Adicionar label `/branch <nome>` ou comentário `<!-- branch: nome -->`

#### Conflitos durante merge automático
- **Causa**: Branch destino avançou após criação da source  
- **Solução**: A esteira tentará rebase automático, senão reportará conflito na issue

#### Workspace poluído com branches antigas
- **Causa**: `cleanup: false` em ambiente compartilhado
- **Solução**: Ativar `cleanup: true` ou limpar manualmente com `git branch -D`
