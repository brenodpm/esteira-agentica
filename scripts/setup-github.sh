#!/usr/bin/env bash
# Setup inicial do repositório GitHub — task11
# Pré-requisito: gh auth login executado

set -euo pipefail

REPO="brenodpm/esteira-agentica"
OWNER="brenodpm"

echo "=== Verificando autenticação ==="
gh auth status

echo ""
echo "=== Labels por épico ==="
gh label create "epic:orquestracao"   --repo "$REPO" --color "#0075ca" --description "Épico: Orquestração Automática de Agentes" --force
gh label create "epic:gestao-tarefas" --repo "$REPO" --color "#e4e669" --description "Épico: Gestão de Tarefas" --force
gh label create "epic:integracao-git" --repo "$REPO" --color "#d93f0b" --description "Épico: Integração com Git" --force
gh label create "epic:metricas"       --repo "$REPO" --color "#0e8a16" --description "Épico: Coleta de Métricas" --force
gh label create "epic:operacao-remota" --repo "$REPO" --color "#5319e7" --description "Épico: Operação Remota" --force

echo ""
echo "=== Labels operacionais ==="
gh label create "blocked"      --repo "$REPO" --color "#b60205" --description "Issue bloqueada por dependência" --force
gh label create "needs-human"  --repo "$REPO" --color "#e99695" --description "Aguarda intervenção humana" --force
gh label create "approved"     --repo "$REPO" --color "#0e8a16" --description "Gate de aprovação: aprovado" --force
gh label create "rejected"     --repo "$REPO" --color "#b60205" --description "Gate de aprovação: rejeitado" --force

echo ""
echo "=== Milestones ==="
gh api "repos/$REPO/milestones" --method POST \
  --field title="Orquestração Automática de Agentes" \
  --field description="Eliminar o humano como orquestrador, automatizando o acionamento e sequenciamento dos agentes de IA."
gh api "repos/$REPO/milestones" --method POST \
  --field title="Gestão de Tarefas" \
  --field description="Organizar features, bugs, milestones e stories em um sistema de gestão integrado à esteira."
gh api "repos/$REPO/milestones" --method POST \
  --field title="Integração com Git" \
  --field description="Automatizar operações de versionamento integradas ao fluxo da esteira."
gh api "repos/$REPO/milestones" --method POST \
  --field title="Coleta de Métricas" \
  --field description="[PRIORIDADE 1] Tornar o custo em tokens visível e controlável, além de auditar qualidade e velocidade do processo."
gh api "repos/$REPO/milestones" --method POST \
  --field title="Operação Remota" \
  --field description="Permitir que o sistema rode de forma autônoma em qualquer máquina sem interação direta do usuário."

echo ""
echo "=== Board (GitHub Project) ==="
PROJECT_URL=$(gh project create --owner "$OWNER" --title "Esteira Agêntica" --format board --json url --jq '.url')
echo "Board criado: $PROJECT_URL"
PROJECT_NUMBER=$(gh project list --owner "$OWNER" --format json --jq '.projects[] | select(.title=="Esteira Agêntica") | .number')

echo ""
echo "=== Issues iniciais ==="

# Épico: Orquestração Automática de Agentes
I1=$(gh issue create --repo "$REPO" \
  --title "Definir protocolo de passagem de contexto entre agentes" \
  --label "epic:orquestracao" --milestone "Orquestração Automática de Agentes" \
  --body "Definir o formato e o mecanismo pelo qual um agente passa contexto para o próximo na esteira." \
  --json number --jq '.number')
I2=$(gh issue create --repo "$REPO" \
  --title "Implementar gate de aprovação humana entre etapas" \
  --label "epic:orquestracao" --milestone "Orquestração Automática de Agentes" \
  --body "O sistema deve pausar e aguardar aprovação do usuário antes de avançar para a próxima etapa." \
  --json number --jq '.number')
I3=$(gh issue create --repo "$REPO" \
  --title "Implementar orquestrador central" \
  --label "epic:orquestracao" --milestone "Orquestração Automática de Agentes" \
  --body "Módulo responsável por sequenciar os agentes conforme o fluxo definido." \
  --json number --jq '.number')

# Épico: Gestão de Tarefas
I4=$(gh issue create --repo "$REPO" \
  --title "Integrar leitura de backlog do GitHub Issues" \
  --label "epic:gestao-tarefas" --milestone "Gestão de Tarefas" \
  --body "O orquestrador deve ler issues do GitHub para determinar o próximo item a ser processado." \
  --json number --jq '.number')
I5=$(gh issue create --repo "$REPO" \
  --title "Implementar atualização automática de status das issues" \
  --label "epic:gestao-tarefas" --milestone "Gestão de Tarefas" \
  --body "O sistema deve mover issues entre colunas do board conforme o progresso da esteira." \
  --json number --jq '.number')

# Épico: Integração com Git
I6=$(gh issue create --repo "$REPO" \
  --title "Implementar criação automática de branches por feature" \
  --label "epic:integracao-git" --milestone "Integração com Git" \
  --body "Ao iniciar uma feature, o sistema cria automaticamente a branch seguindo o gitflow configurado." \
  --json number --jq '.number')
I7=$(gh issue create --repo "$REPO" \
  --title "Implementar criação automática de Pull Requests" \
  --label "epic:integracao-git" --milestone "Integração com Git" \
  --body "Ao finalizar uma feature, o sistema abre PR para develop com descrição gerada automaticamente." \
  --json number --jq '.number')

# Épico: Coleta de Métricas
I8=$(gh issue create --repo "$REPO" \
  --title "[P1] Implementar coleta de custo em tokens por agente" \
  --label "epic:metricas" --milestone "Coleta de Métricas" \
  --body "Registrar o consumo de tokens de cada agente por execução. Prioridade 1." \
  --json number --jq '.number')
I9=$(gh issue create --repo "$REPO" \
  --title "[P1] Implementar coleta de custo em tokens por feature" \
  --label "epic:metricas" --milestone "Coleta de Métricas" \
  --body "Agregar o custo total em tokens do ciclo completo de uma feature. Prioridade 1." \
  --json number --jq '.number')
I10=$(gh issue create --repo "$REPO" \
  --title "Implementar registro de tempo de execução por etapa" \
  --label "epic:metricas" --milestone "Coleta de Métricas" \
  --body "Registrar o tempo de início e fim de cada etapa da esteira." \
  --json number --jq '.number')

# Épico: Operação Remota
I11=$(gh issue create --repo "$REPO" \
  --title "Garantir que toda interação com o usuário ocorra via GitHub" \
  --label "epic:operacao-remota" --milestone "Operação Remota" \
  --body "Aprovações, notificações e status devem ser acessíveis remotamente via GitHub Issues/Projects, sem acesso direto à máquina." \
  --json number --jq '.number')

echo ""
echo "=== Adicionando issues ao board ==="
for ISSUE_NUM in $I1 $I2 $I3 $I4 $I5 $I6 $I7 $I8 $I9 $I10 $I11; do
  ISSUE_ID=$(gh api "repos/$REPO/issues/$ISSUE_NUM" --jq '.node_id')
  gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "https://github.com/$REPO/issues/$ISSUE_NUM"
  echo "  Issue #$ISSUE_NUM adicionada ao board"
done

echo ""
echo "=== Setup concluído ==="
echo "Verifique:"
echo "  gh label list --repo $REPO"
echo "  gh api repos/$REPO/milestones"
echo "  gh project list --owner $OWNER"
echo "  gh issue list --repo $REPO --state open"
echo ""
echo "ATENÇÃO: Renomear coluna 'Todo' para 'Backlog' via UI do GitHub (não suportado via CLI)."
