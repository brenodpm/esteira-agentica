# GitHub Setup — Pendente

Status: pending-execution
Owner: engineering-agent
Last updated: 2026-05-14T22:39:00-03:00

## Pré-requisito

```bash
gh auth login
# Escolher: GitHub.com → SSH → autenticar via browser
```

## 1. Labels por épico

Criar as seguintes labels no repositório `brenodpm/esteira-agentica`:

```bash
gh label create "epic:orquestracao" --color "#0075ca" --description "Épico: Orquestração Automática de Agentes"
gh label create "epic:gestao-tarefas" --color "#e4e669" --description "Épico: Gestão de Tarefas"
gh label create "epic:integracao-git" --color "#d93f0b" --description "Épico: Integração com Git"
gh label create "epic:metricas" --color "#0e8a16" --description "Épico: Coleta de Métricas"
gh label create "epic:operacao-remota" --color "#5319e7" --description "Épico: Operação Remota"
```

## 2. Milestones (um por épico)

```bash
gh api repos/brenodpm/esteira-agentica/milestones --method POST --field title="Orquestração Automática de Agentes" --field description="Eliminar o humano como orquestrador, automatizando o acionamento e sequenciamento dos agentes de IA."
gh api repos/brenodpm/esteira-agentica/milestones --method POST --field title="Gestão de Tarefas" --field description="Organizar features, bugs, milestones e stories em um sistema de gestão integrado à esteira."
gh api repos/brenodpm/esteira-agentica/milestones --method POST --field title="Integração com Git" --field description="Automatizar operações de versionamento integradas ao fluxo da esteira."
gh api repos/brenodpm/esteira-agentica/milestones --method POST --field title="Coleta de Métricas" --field description="[PRIORIDADE 1] Tornar o custo em tokens visível e controlável, além de auditar qualidade e velocidade do processo."
gh api repos/brenodpm/esteira-agentica/milestones --method POST --field title="Operação Remota" --field description="Permitir que o sistema rode de forma autônoma em qualquer máquina sem interação direta do usuário."
```

## 3. Issues iniciais por épico

### Épico: Orquestração Automática de Agentes
```bash
gh issue create --title "Definir protocolo de passagem de contexto entre agentes" --label "epic:orquestracao" --milestone "Orquestração Automática de Agentes" --body "Definir o formato e o mecanismo pelo qual um agente passa contexto para o próximo na esteira."
gh issue create --title "Implementar gate de aprovação humana entre etapas" --label "epic:orquestracao" --milestone "Orquestração Automática de Agentes" --body "O sistema deve pausar e aguardar aprovação do usuário antes de avançar para a próxima etapa."
gh issue create --title "Implementar orquestrador central" --label "epic:orquestracao" --milestone "Orquestração Automática de Agentes" --body "Módulo responsável por sequenciar os agentes conforme o fluxo definido."
```

### Épico: Gestão de Tarefas
```bash
gh issue create --title "Integrar leitura de backlog do GitHub Issues" --label "epic:gestao-tarefas" --milestone "Gestão de Tarefas" --body "O orquestrador deve ler issues do GitHub para determinar o próximo item a ser processado."
gh issue create --title "Implementar atualização automática de status das issues" --label "epic:gestao-tarefas" --milestone "Gestão de Tarefas" --body "O sistema deve mover issues entre colunas do board conforme o progresso da esteira."
```

### Épico: Integração com Git
```bash
gh issue create --title "Implementar criação automática de branches por feature" --label "epic:integracao-git" --milestone "Integração com Git" --body "Ao iniciar uma feature, o sistema cria automaticamente a branch seguindo o gitflow configurado."
gh issue create --title "Implementar criação automática de Pull Requests" --label "epic:integracao-git" --milestone "Integração com Git" --body "Ao finalizar uma feature, o sistema abre PR para develop com descrição gerada automaticamente."
```

### Épico: Coleta de Métricas
```bash
gh issue create --title "[P1] Implementar coleta de custo em tokens por agente" --label "epic:metricas" --milestone "Coleta de Métricas" --body "Registrar o consumo de tokens de cada agente por execução. Prioridade 1."
gh issue create --title "[P1] Implementar coleta de custo em tokens por feature" --label "epic:metricas" --milestone "Coleta de Métricas" --body "Agregar o custo total em tokens do ciclo completo de uma feature. Prioridade 1."
gh issue create --title "Implementar registro de tempo de execução por etapa" --label "epic:metricas" --milestone "Coleta de Métricas" --body "Registrar o tempo de início e fim de cada etapa da esteira."
```

### Épico: Operação Remota
```bash
gh issue create --title "Garantir que toda interação com o usuário ocorra via GitHub" --label "epic:operacao-remota" --milestone "Operação Remota" --body "Aprovações, notificações e status devem ser acessíveis remotamente via GitHub Issues/Projects, sem acesso direto à máquina."
```

## 4. GitHub Project (board)

```bash
gh project create --owner brenodpm --title "Esteira Agêntica" --format board
```

Após criar o projeto, adicionar todas as issues ao board. O board padrão já vem com colunas Todo / In Progress / Done — renomear "Todo" para "Backlog".
