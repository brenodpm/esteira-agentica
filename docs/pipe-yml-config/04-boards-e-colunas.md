# Configuração de Boards e Colunas

Boards são o núcleo organizacional da esteira que implementam workflows de desenvolvimento através de colunas. Cada board representa um tipo específico de trabalho (como user stories, bugs ou débitos técnicos) e sincroniza automaticamente com um GitHub Project V2 correspondente. 

Os boards definem como as issues fluem desde sua criação até conclusão, estabelecendo responsabilidades por etapa, critérios de transição e integrações com git. Uma issue sempre existe dentro de um board e se move entre suas colunas conforme o trabalho progride, seja através de agentes automatizados ou intervenção manual.

## Estrutura Base

```yaml
boards:
  bugs: bug                    # ID do board para bugs (usado internamente)
  needs: debito                # ID do board para demandas de humanos/agentes
  create-remote-boards: true   # Cria boards remotos automaticamente se não existirem
  allow-del-remote-issue: true # Permite deletar issues remotas

  <board-id>:                  # Define um novo board
    name: "..."                # Nome no GitHub Projects
    todo: backlog              # ID da coluna inicial
    priority: 0                # Ordem de processamento (0 = mais alta)
    flow: epic                 # Gitflow associado
    parallel: false            # Processa uma issue por vez ou em paralelo
    columns:
      <col-id>:               # Define uma coluna dentro do board
        # ... configuração da coluna
```

## Configurações de Board

Cada board define um workflow completo para um tipo específico de demanda. A configuração determina como issues são processadas, em qual ordem, e como se integram com git.

| Campo | Descrição | Exemplo | Observações |
|-------|-----------|---------|-------------|
| `name` | Nome visível no GitHub Projects | `"User Stories"` | Deve ser único no repositório |
| `todo` | ID da coluna onde issues novas entram | `backlog` | Coluna deve existir em `columns` |
| `priority` | Ordem de processamento (0 = maior prioridade) | `0`, `1`, `2` | Boards com menor número executam primeiro |
| `flow` | Gitflow usado por issues deste board | `feature`, `epic`, `bugfix` | Determina padrão de branch criada |
| `parallel` | Se `false`, processa uma issue por vez | `true`/`false` | `false` evita conflitos em mudanças dependentes |

A **prioridade** é fundamental para evitar conflitos: bugs (priority 0) executam antes de features (priority 2), garantindo que correções críticas não sejam bloqueadas por desenvolvimento novo.

## Configurações de Coluna

Colunas representam estados específicos no ciclo de vida de uma issue. Cada coluna define quem é responsável pelo trabalho (agente ou humano), que ações devem ser executadas, e para onde a issue deve transitar após conclusão.

```yaml
columns:
  backlog:                     # ID único da coluna
    name: Backlog              # Nome visível no GitHub Projects
    desc: "..."                # Descrição do que acontece aqui
    agent: requirements        # Agente responsável (se ausente = manual)
    effort: high               # Nível de esforço (low, medium, high)
    gitevents: [create, merge] # Eventos git executados aqui
    acao: "..."                # Instrução para o agente
    git_commit: true           # Faz commit das alterações
    git_merge: true            # Envolve criação de PR/merge
    wait_children: false       # Aguarda issues filhas terminarem
    allow-overwrite: true      # Permite `/effort` na issue sobrescrever
    change:                    # Transições para outras colunas
      advance: proxima_coluna
      reprovar: backlog
      falha: desenvolvimento
      bloquear: blocked
      cancelar: cancelado
```

**Colunas manuais** (sem `agent`) representam pontos de decisão humana, como aprovações ou revisões. **Colunas automatizadas** (com `agent`) executam trabalho através de agentes especializados, seguindo a instrução definida em `acao`.

### Eventos Git (gitevents)

Os eventos git definem integrações com controle de versão que acontecem quando uma issue entra ou sai da coluna. Estes eventos automatizam o fluxo de branches e merge requests.

- **create**: Cria uma nova branch quando a issue entra na coluna
  - Usa o gitflow configurado no board (`feature/`, `epic/`, `bugfix/`)
  - Nomenclatura: `{gitflow}/{issue-id}-{issue-slug}`
  - Falha se branch já existe (use `keep` para reutilizar)

- **keep**: Mantém branch existente sem criar nova (comportamento padrão)
  - Útil para colunas intermediárias que não requerem nova branch
  - Preserva contexto de desenvolvimento contínuo
  - Recomendado para colunas de revisão ou validação

- **merge**: Solicita merge request quando a issue sai da coluna
  - Cria PR automaticamente para branch configurada no gitflow
  - Depende de `git_merge: true` na configuração da coluna
  - Usado tipicamente na última coluna de desenvolvimento

**Exemplo de fluxo**: Uma issue em board `story` com `flow: epic` passando por coluna com `gitevents: [create]` resulta em branch `epic/123-minha-story`.

### Transições (change)

As transições definem o comportamento da issue após o agente ou humano completar o trabalho na coluna atual. Cada transição representa um resultado diferente e determina a coluna de destino.

- **advance**: Transição normal quando trabalho é concluído com sucesso
  - Issue move para próxima coluna no fluxo padrão
  - Indica progressão esperada no workflow
  - Exemplo: desenvolvimento concluído → revisão de código

- **reprovar**: Retorna issue para revisão por não atender critérios
  - Tipicamente volta para coluna anterior ou específica
  - Indica necessidade de retrabalho ou correções
  - Exemplo: código rejeitado na revisão → volta para desenvolvimento

- **cancelar**: Move issue para estado final quando não deve prosseguir
  - Issue não será mais processada neste ciclo
  - Diferente de reprovar: não há intenção de retrabalho imediato
  - Exemplo: requisito cancelado pelo stakeholder

- **falha**: Retorna issue quando testes automatizados ou validações falham
  - Diferente de reprovar: falha é técnica, reprovar é critério de qualidade
  - Permite retry automático ou intervenção técnica
  - Exemplo: build falha → volta para desenvolvimento

- **bloquear**: Move issue para estado de espera por dependência externa
  - Issue aguarda resolução de bloqueio antes de prosseguir
  - Permite rastreamento de impedimentos
  - Exemplo: aguardando aprovação de infraestrutura

**Cenário exemplo**: Uma issue na coluna "desenvolvimento" pode:
- `advance` → "code-review" (código implementado)
- `falha` → "desenvolvimento" (testes falharam)
- `bloquear` → "blocked" (dependência externa)
- `cancelar` → "cancelado" (requisito removido)

## Exemplo Prático: Board "User Stories"

Este exemplo demonstra um board completo para gerenciar user stories, desde levantamento de requisitos até entrega final. Observe como cada coluna tem responsabilidade específica e transições bem definidas.

```yaml
story:
  name: "User Stories"          # Nome visível no GitHub Projects
  todo: backlog                 # Issues novas entram no backlog
  priority: 3                   # Executa após bugs (0) e débitos (1)
  flow: epic                    # Cria branches epic/123-nome-da-story
  columns:
    backlog:
      name: Backlog
      desc: "Story aguardando início de análise"
      # Coluna manual - humano decide quando iniciar
      change:
        advance: requisitos     # Humano aprova início
        cancelar: cancelado     # Story não é mais necessária

    requisitos:
      name: "Requisitos"
      desc: "Levantamento de requisitos funcionais e não-funcionais"
      agent: requirements       # Agente automatizado
      gitevents: [create]       # Cria branch epic/123-minha-story
      acao: "Entender demanda, entrevistar usuário, criar documentações"
      change:
        advance: validacao-negocial    # Documentação criada
        falha: backlog                 # Problema no levantamento
        bloquear: blocked              # Aguardando stakeholder

    validacao-negocial:
      name: "Validação"
      desc: "Revisão humana da documentação de requisitos"
      # Coluna manual - stakeholder valida
      change:
        advance: arquitetura    # Requisitos aprovados
        reprovar: requisitos    # Necessita correções

    arquitetura:
      name: "Arquitetura"
      desc: "Definição de arquitetura técnica e design"
      agent: architecture       # Agente especializado
      effort: high              # Trabalho complexo
      acao: "Definir arquitetura técnica baseada nos requisitos"
      change:
        advance: desenvolvimento
        reprovar: requisitos    # Requisitos insuficientes
        bloquear: blocked       # Dependência técnica

    desenvolvimento:
      name: "Desenvolvimento"
      desc: "Implementação seguindo arquitetura aprovada"
      agent: engineering        # Agente de desenvolvimento
      effort: high
      gitevents: [merge]        # Cria PR quando termina
      acao: "Implementar conforme arquitetura aprovada"
      git_commit: true          # Commits são feitos
      git_merge: true           # PR é criado
      change:
        advance: concluido      # Implementação finalizada
        falha: desenvolvimento  # Testes falharam
        reprovar: arquitetura   # Design precisa revisão

    concluido:
      name: "Concluído"
      desc: "Story entregue e integrada"
      # Estado final - não há transições
```

### Fluxo de uma Issue

Uma story típica segue este caminho:

1. **Criação**: Issue entra em `backlog` automaticamente
2. **Início**: Humano move para `requisitos` (advance)
3. **Análise**: Agent requirements cria branch e documenta requisitos
4. **Validação**: Humano aprova ou rejeita documentação
5. **Design**: Agent architecture define solução técnica
6. **Implementação**: Agent engineering codifica e cria PR
7. **Conclusão**: Issue finaliza em `concluido`

### Cenários de Exceção

- **Requisitos insuficientes**: `validacao-negocial` → `reprovar` → `requisitos`
- **Bloqueio técnico**: `arquitetura` → `bloquear` → `blocked`
- **Falha de testes**: `desenvolvimento` → `falha` → `desenvolvimento`
- **Story cancelada**: qualquer coluna → `cancelar` → `cancelado`

## Boas Práticas

1. **Ordene colunas conforme o fluxo natural** de trabalho
2. **Cada coluna com `agent`** deve ter uma `acao` clara
3. **Use `priority`** para controlar qual board é processado primeiro
4. **Colunas manuais** (sem agente) são revisão humana
5. **`wait_children`** é útil quando há dependências (ex: épicos aguardam stories)
6. **Mantenha nomes de coluna curtos** (compatível com GitHub Projects)
