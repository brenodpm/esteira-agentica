# Exemplos Práticos de Configuração

Guias passo-a-passo para cenários comuns.

## Cenário 1: Adicionar um Novo Board

**Caso de uso**: Você quer criar um board "Pesquisa" para tarefas de investigação e prototipagem.

### Passo 1: Definir o ID do Board

```yaml
boards:
  research:          # ID único do board
    name: "Pesquisa e Prototipagem"
    todo: backlog    # Coluna inicial
    priority: 4      # Executado depois de tasks, stories, bugs
    flow: feature    # Usa o gitflow de features
```

### Passo 2: Criar as Colunas

```yaml
  research:
    name: "Pesquisa e Prototipagem"
    todo: backlog
    priority: 4
    flow: feature
    columns:
      backlog:
        name: Backlog
        desc: "Pesquisa aberta, aguardando início"
        change:
          advance: investigacao

      investigacao:
        name: "Investigação"
        agent: architecture
        effort: high
        gitevents: [create]
        acao: "Pesquisar tecnologia/padrão, documentar achados"
        change:
          advance: prototipo

      prototipo:
        name: "Prototipo"
        agent: engineering
        effort: medium
        gitevents: [merge]
        acao: "Implementar prototipo de prova de conceito"
        change:
          advance: concluido

      concluido:
        name: "Concluído"
```

### Passo 3: Resultado

Próxima execução da esteira:
- Cria um novo GitHub Project chamado "Pesquisa e Prototipagem"
- Cria as colunas Backlog, Investigação, Prototipo, Concluído
- Issues podem ser movidas entre colunas conforme avançam

---

## Cenário 2: Customizar Níveis de Effort

**Caso de uso**: Seu time precisa de análise muito profunda em requisitos, mas implementação rápida.

### Passo 1: Definir Models Customizados

```yaml
effort:
  low:
    model: claude-haiku-4.5
    effort: low
  medium:
    model: claude-sonnet-4
    effort: medium
  high:
    model: claude-sonnet-4
    effort: high
  ultra:               # Novo nível customizado
    model: claude-sonnet-4
    effort: high
```

### Passo 2: Usar em Colunas Críticas

```yaml
boards:
  story:
    columns:
      requisitos:
        name: "Requisitos"
        agent: requirements
        effort: high         # Máxima profundidade
        allow-overwrite: false
        acao: "Análise profunda dos requisitos"
        change:
          advance: arquitetura

      desenvolvimento:
        name: "Desenvolvimento"
        agent: engineering
        effort: low          # Implementação direta
        allow-overwrite: false
        acao: "Implementar conforme aprovado"
        change:
          advance: testes
```

### Resultado

- Coluna de requisitos sempre usa análise profunda
- Coluna de desenvolvimento usa modelo rápido (reduz custos)

---

## Cenário 3: Criar um Gitflow Customizado

**Caso de uso**: Você quer um fluxo de hotfix que vai direto para produção.

### Passo 1: Definir o Gitflow

```yaml
git:
  flow:
    base: main
    cleanup: true

    hotfix:
      prefix: hotfix
      description: "Correção crítica para produção"
      create: main          # Cria da main (em produção)
      merge: main           # Volta direto para main
```

### Passo 2: Criar o Board de Hotfix

```yaml
boards:
  hotfix:
    name: "Hotfixes"
    todo: backlog
    priority: 0              # MÁXIMA prioridade
    flow: hotfix
    parallel: false          # Uma hotfix por vez
    columns:
      backlog:
        name: Backlog
        desc: "Hotfix aberta"
        change:
          advance: correcao

      correcao:
        name: "Correção"
        agent: engineering
        gitevents: [create]
        acao: "Corrigir bug crítico com testes"
        change:
          advance: code-review

      code-review:
        name: "Code Review"
        desc: "Revisão rápida do hotfix"
        change:
          advance: deploy
          reprovar: correcao

      deploy:
        name: "Deploy"
        agent: devops
        gitevents: [merge]
        acao: "Deploy imediato para produção"
        change:
          advance: concluido

      concluido:
        name: "Concluído"
```

### Resultado

- Hotfixes são sempre processadas primeiro (`priority: 0`)
- Uma por vez (`parallel: false`)
- Branch criada da main, corrigida, revisada e mergeada direto

---

## Cenário 4: Board com Validação Humana

**Caso de uso**: Você quer que todas as especificações sejam validadas por um human antes de ir para arquitetura.

### Configuração

```yaml
boards:
  story:
    columns:
      requisitos:
        name: "Requisitos"
        agent: requirements
        gitevents: [create]
        acao: "Levantar requisitos"
        change:
          advance: validacao

      validacao:
        name: "Validação"
        desc: "Humano valida requisitos"
        # Sem 'agent' → coluna manual
        change:
          advance: arquitetura    # Se aprovado
          reprovar: requisitos    # Se precisa ajuste

      arquitetura:
        name: "Arquitetura"
        agent: architecture
        acao: "Definir design"
        change:
          advance: desenvolvimento
```

### Resultado

- Coluna "Validação" fica parada aguardando humano
- Humano move a issue para "Arquitetura" (approve) ou volta para "Requisitos" (reject)

---

## Cenário 5: Dependência Entre Boards

**Caso de uso**: Um épico só avança quando TODAS as user stories estão concluídas.

### Configuração

```yaml
boards:
  epic:
    columns:
      aguardando-stories:
        name: "Aguardando Stories"
        desc: "Épico aguarda conclusão de todas as stories"
        wait_children: true  # ← Chave!
        change:
          advance: release

  story:
    columns:
      concluido:
        name: "Concluído"
```

### Como Funciona

1. Épico é bloqueado com as stories via label `/blocked_by story/123`
2. Épico entra em "Aguardando Stories" com `wait_children: true`
3. Esteira aguarda todas as stories concluídas
4. Após todas terminarem, épico move automaticamente para "Release"

---

## Cenário 6: Esforço Variável por Issue

**Caso de uso**: A maioria das tasks usa esforço medium, mas algumas complexas precisam de análise deep.

### Configuração

```yaml
boards:
  task:
    columns:
      desenvolvimento:
        name: "Desenvolvimento"
        agent: engineering
        effort: medium           # Padrão
        allow-overwrite: true    # Permite override
        acao: "Implementar task"
        change:
          advance: testes
```

### Como Usar

No corpo da issue, adicione:

```
/effort high
```

Resultado:
- Esta issue usa `claude-sonnet-4` com `high` effort
- Outras tasks continuam com `medium` effort
- Economia de tokens em tarefas rotineiras, análise profunda onde necessário

---

## Checklist: Validar seu pipe.yml

- [ ] Todos os boards têm `name` e `todo` definidos
- [ ] Colunas iniciais correspondem ao `todo` de cada board
- [ ] Cada coluna com `agent` tem `acao` definida
- [ ] Transições de `change` usam IDs de colunas que existem
- [ ] Gitflows referenciados em `flow` estão definidos em `git.flow`
- [ ] Prefixos de gitflow não têm conflitos
- [ ] `effort` levels têm `model` e `effort` definidos
- [ ] `priority` dos boards é incrementando (0, 1, 2, ...)
