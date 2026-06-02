#!/usr/bin/env bash
# Setup inicial do repositório GitHub para uso com a esteira agêntica.
# Cria labels operacionais e o board (GitHub Project).
# As issues são criadas pela própria esteira ou manualmente pelo usuário.
#
# Uso: bash scripts/setup-github.sh [owner/repo]
# Se não informado, lê git.repo do esteira.yml.

set -euo pipefail

# --- Resolve repo ---
if [ -n "${1:-}" ]; then
  REPO="$1"
else
  REPO=$(python3 -c "
import yaml, sys
try:
    cfg = yaml.safe_load(open('esteira.yml'))
    print(cfg['git']['repo'])
except Exception as e:
    print('', end='')
")
fi

if [ -z "$REPO" ]; then
  echo "Erro: informe o repositório como argumento ou configure git.repo no esteira.yml"
  exit 1
fi

OWNER="${REPO%%/*}"

echo "=== Verificando autenticação ==="
gh auth status

echo ""
echo "=== Labels operacionais ==="
gh label create "blocked"       --repo "$REPO" --color "#b60205" --description "Issue bloqueada por dependência" --force
gh label create "needs-human"   --repo "$REPO" --color "#e99695" --description "Aguarda intervenção humana" --force
gh label create "approved"      --repo "$REPO" --color "#0e8a16" --description "Gate de aprovação: aprovado" --force
gh label create "rejected"      --repo "$REPO" --color "#b60205" --description "Gate de aprovação: rejeitado" --force
gh label create "improvement"   --repo "$REPO" --color "#a2eeef" --description "Melhoria proposta pelo optimizer" --force

echo ""
echo "=== Labels de board (colunas) ==="
# Lê os ids de colunas do esteira.yml e cria uma label para cada
python3 - "$REPO" << 'PYEOF'
import sys, subprocess, yaml

repo = sys.argv[1]
cfg = yaml.safe_load(open("esteira.yml"))
created = set()
for board_id, board in cfg.get("boards", {}).items():
    for col_id, col in board.get("columns", {}).items():
        if col_id not in created:
            name = col.get("name", col_id)
            subprocess.run([
                "gh", "label", "create", col_id,
                "--repo", repo,
                "--color", "#ededed",
                "--description", f"Coluna do board: {name}",
                "--force"
            ], check=True)
            print(f"  label '{col_id}' ({name})")
            created.add(col_id)
PYEOF

echo ""
echo "=== Board (GitHub Project) ==="
EXISTING=$(gh project list --owner "$OWNER" --format json --jq '.projects[] | select(.title=="Esteira Agêntica") | .number' 2>/dev/null || echo "")
if [ -n "$EXISTING" ]; then
  echo "Board 'Esteira Agêntica' já existe (número $EXISTING)"
else
  gh project create --owner "$OWNER" --title "Esteira Agêntica"
  echo "Board criado"
fi

echo ""
echo "=== Setup concluído ==="
echo "Próximos passos:"
echo "  1. Crie issues no GitHub com a label da coluna inicial (ex: 'backlog')"
echo "  2. Execute: python -m src"
