"""Geração do prompt de execução do agente."""

import json
from pathlib import Path

from src.log import log

AGENTS_DIR = Path(".kiro/agents")
BOARDS_DIR = Path(".pipe/boards")


def _load_agent(name: str) -> dict:
    path = AGENTS_DIR / f"{name}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def _resolve_branch_name(task: dict, flow: dict, flow_type: str) -> str:
    prefix = flow[flow_type]["prefix"]
    issue_id = task["id"]
    slug = Path(task["path"]).stem.split("-", 1)[1] if "-" in Path(task["path"]).stem else str(issue_id)
    return f"{prefix}/{issue_id}-{slug}"


def _resolve_branch(config: dict, task: dict, board: dict) -> str:
    flow_type = board.get("flow", "feature")
    flow = config["git"]["flow"]
    return _resolve_branch_name(task, flow, flow_type)


def _resolve_origin_branch(config: dict, board: dict) -> str:
    flow_type = board.get("flow", "feature")
    flow = config["git"]["flow"]
    return flow[flow_type].get("create", flow.get("base", "main"))


def _resolve_merge_branch(config: dict, board: dict) -> str:
    flow_type = board.get("flow", "feature")
    flow = config["git"]["flow"]
    return flow[flow_type].get("merge", flow.get("base", "main"))


def build_prompt(config: dict, task: dict) -> str:
    board_id = task["board_id"]
    board = config["boards"][board_id]
    column = board["columns"][task["column"]]

    agent_name = column.get("agent")
    agent = _load_agent(agent_name) if agent_name else {}
    model = agent.get("model")
    effort = column.get("effort")
    gitevents = column.get("gitevents", [])

    branch_name = _resolve_branch(config, task, board)
    origin_branch = _resolve_origin_branch(config, board)
    merge_branch = _resolve_merge_branch(config, board)
    base_branch = config["git"]["flow"].get("base", "main")

    create_branch = "create" in gitevents
    do_merge = "merge" in gitevents

    lines = []

    # Cabeçalho de configuração
    if model:
        lines.append(f"/model {model}")
    if effort:
        lines.append(f"/effort {effort}")
    lines.append(f"/context {task['path']}")
    lines.append(f"/knowledge {task['history_path']}")
    lines.append("")
    lines.append("")

    # Etapa e tarefa
    lines.append(f"Etapa: {column.get('name', task['column'])}")
    lines.append(f"Tarefa: {task['name']}")
    lines.append("")

    # Instruções
    lines.append("Faça:")
    if create_branch:
        lines.append(f"- [ ] criar branch {branch_name} a partir da {origin_branch}")
    else:
        lines.append(f"- [ ] usar branch {branch_name}")
    lines.append(f"- [ ] executar tarefa `{task['path']}`")
    lines.append(f"- [ ] checar se as tarefas em `/blocked_by` foram concluidas, se não foram, anotar comentário em {task['write_path']} e encerrar processamento")
    lines.append(f"- [ ] se houver dúvidas escrever as dúvidas no write e adicinar /need_human no body da tarefa")
    needs_board = config.get("boards_meta", {}).get("needs", "debito")
    needs_dir = str(BOARDS_DIR / needs_board / "backlog")
    lines.append(f"- [ ] se houver demanda bloqueante, abrir um card no board {needs_dir}")
    lines.append("- [ ] fazer commit e push")
    if do_merge:
        lines.append(f"- [ ] criar merge request para {merge_branch}")
    lines.append(f"- [ ] Anotar um resumo curto do que foi executado em `{task['write_path']}`")
    lines.append(f"- [ ] fazer checkout para {base_branch} e apagar todas as branchs locais ()")
    lines.append("")
    lines.append("")

    # Transições
    lines.append("Após conclusão da tarefa mova o issue")
    change = column.get("change", {})
    for condition, target_col in change.items():
        target_dir = str(BOARDS_DIR / board_id / target_col)
        lines.append(f"se {condition} >> mover para {target_dir}")

    return "\n".join(lines)


def run_agent(config: dict, task: dict):
    """Gera e imprime o prompt do agente (sem execução real por enquanto)."""
    prompt = build_prompt(config, task)
    print(prompt)
