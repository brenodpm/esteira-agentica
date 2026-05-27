Status: approved
Owner: engineering-agent
Last updated: 2026-05-27

## Inputs
- docs/01-requirements/github-setup.md
- docs/02-architecture/adr-004-mecanismo-bloqueio-tasks.md
- docs/02-architecture/adr-005-interacao-humano-issues.md
- docs/02-architecture/adr-006-prioridade-execucao-tasks.md
- docs/04-tasks/task01-estrutura-projeto.md

## Descrição

Executar o setup inicial do repositório GitHub: criar labels por épico e labels operacionais do sistema, criar milestones por épico, criar o board (GitHub Project) e criar as issues iniciais por épico. Pré-requisito para qualquer execução da esteira.

## Tipo
- infra

## Escopo técnico

### Labels por épico (5)
```bash
gh label create "epic:orquestracao" --color "#0075ca" --description "Épico: Orquestração Automática de Agentes"
gh label create "epic:gestao-tarefas" --color "#e4e669" --description "Épico: Gestão de Tarefas"
gh label create "epic:integracao-git" --color "#d93f0b" --description "Épico: Integração com Git"
gh label create "epic:metricas" --color "#0e8a16" --description "Épico: Coleta de Métricas"
gh label create "epic:operacao-remota" --color "#5319e7" --description "Épico: Operação Remota"
```

### Labels operacionais do sistema (4)
```bash
gh label create "blocked" --color "#b60205" --description "Issue bloqueada por dependência"
gh label create "needs-human" --color "#e99695" --description "Aguarda intervenção humana"
gh label create "approved" --color "#0e8a16" --description "Gate de aprovação: aprovado"
gh label create "rejected" --color "#b60205" --description "Gate de aprovação: rejeitado"
```

### Milestones (um por épico)
```bash
gh api repos/brenodpm/esteira-agentica/milestones --method POST --field title="Orquestração Automática de Agentes" --field description="Eliminar o humano como orquestrador."
gh api repos/brenodpm/esteira-agentica/milestones --method POST --field title="Gestão de Tarefas" --field description="Sistema de gestão integrado à esteira."
gh api repos/brenodpm/esteira-agentica/milestones --method POST --field title="Integração com Git" --field description="Automatizar operações de versionamento."
gh api repos/brenodpm/esteira-agentica/milestones --method POST --field title="Coleta de Métricas" --field description="[P1] Custo em tokens visível e controlável."
gh api repos/brenodpm/esteira-agentica/milestones --method POST --field title="Operação Remota" --field description="Sistema autônomo sem acesso direto à máquina."
```

### Board (GitHub Project)
```bash
gh project create --owner brenodpm --title "Esteira Agêntica" --format board
# Renomear coluna "Todo" para "Backlog" via UI ou API após criação
```

### Issues iniciais
Criar as issues listadas em `docs/01-requirements/github-setup.md` (seção 3) e adicioná-las ao board.

## Fora de escopo

- Configuração de branch protection rules
- Configuração de webhooks
- Criação de ambientes (environments) no GitHub

## Critério de aceite (DoD)

- [ ] Labels por épico existem no repositório (verificar via `gh label list`)
- [ ] Labels operacionais `blocked`, `needs-human`, `approved`, `rejected` existem
- [ ] 5 milestones criados, um por épico
- [ ] Board "Esteira Agêntica" criado com colunas Backlog / In Progress / Done
- [ ] Issues iniciais criadas e associadas aos milestones e labels corretos
- [ ] `gh auth status` confirma autenticação antes de executar

## Dependências

- Nenhuma dependência de código (task de infra independente)
- Pré-requisito: `gh auth login` executado na máquina

## Ordem sugerida

11 — pode ser executada a qualquer momento após autenticação do `gh`; não depende de nenhuma task de código
