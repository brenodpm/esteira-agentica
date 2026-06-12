"""Geração do prompt de execução do agente."""

import json
import re
import subprocess
from pathlib import Path

from src.log import log

AGENTS_DIR = Path(".kiro/agents")
BOARDS_DIR = Path(".pipe/boards")
LOGS_DIR = Path("logs")


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


def _parse_effort_tag(task_path: str) -> str | None:
    """Lê o arquivo da issue e extrai o valor da tag /effort se presente."""
    p = Path(task_path)
    if not p.exists():
        return None
    for line in p.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("/effort"):
            parts = stripped.split()
            if len(parts) >= 2:
                return parts[1]
    return None


def build_prompt(config: dict, task: dict) -> str:
    board_id = task["board_id"]
    board = config["boards"][board_id]
    column = board["columns"][task["column"]]

    agent_name = column.get("agent")
    agent = _load_agent(agent_name) if agent_name else {}

    # Resolução de model/effort (precedência: agent → coluna → tag /effort)
    model = agent.get("model")
    effort = column.get("effort") or agent.get("effort")

    # Se allow-overwrite, buscar tag /effort na issue
    if column.get("allow-overwrite", False):
        tag_effort = _parse_effort_tag(task["path"])
        if tag_effort and tag_effort in config.get("effort", {}):
            effort_map = config["effort"][tag_effort]
            model = effort_map.get("model", model)
            effort = effort_map.get("effort", effort)

    gitevents = column.get("gitevents", [])

    branch_name = _resolve_branch(config, task, board)
    origin_branch = _resolve_origin_branch(config, board)
    merge_branch = _resolve_merge_branch(config, board)
    base_branch = config["git"]["flow"].get("base", "main")

    create_branch = "create" in gitevents
    do_merge = "merge" in gitevents

    lines = []

    # Cabeçalho
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


def _parse_credits(output: str) -> dict:
    """Extrai credits e time da saída do kiro CLI."""
    match = re.search(r"Credits:\s*([\d.]+)\s*.*?Time:\s*(.+?)$", output, re.MULTILINE)
    if match:
        return {"credits": match.group(1), "time": match.group(2).strip()}
    return {}


def _agent_log_path(task: dict) -> Path:
    """Retorna path do log: logs/<issue_id>/yyyyMMddHHmmss-<board_id>-<col_id>-<agent>.log"""
    from datetime import datetime
    board_id = task["board_id"]
    col_id = task["column"]
    agent_name = task.get("_agent", "unknown")
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return LOGS_DIR / str(task["id"]) / f"{ts}-{board_id}-{col_id}-{agent_name}.log"


def run_agent(config: dict, task: dict):
    """Executa o agente via kiro-cli e salva output no log."""
    board = config["boards"][task["board_id"]]
    column = board["columns"][task["column"]]
    agent_name = column.get("agent", "unknown")
    task["_agent"] = agent_name

    prompt = build_prompt(config, task)
    timeout = config["pipe"].get("agent", {}).get("timeout", 1800)

    log.info("Executando agente '%s' para #%s...", agent_name, task["id"])

    cmd = ["kiro-cli", "chat", "--agent", agent_name, "--no-interactive", "-a"]

    # Model na CLI
    board = config["boards"][task["board_id"]]
    column = board["columns"][task["column"]]
    agent_cfg = _load_agent(column.get("agent", ""))
    resolved_model = agent_cfg.get("model")
    col_effort = column.get("effort") or agent_cfg.get("effort")
    if column.get("allow-overwrite", False):
        tag_effort = _parse_effort_tag(task["path"])
        if tag_effort and tag_effort in config.get("effort", {}):
            effort_map = config["effort"][tag_effort]
            resolved_model = effort_map.get("model", resolved_model)
    if resolved_model:
        cmd += ["--model", resolved_model]

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        output = f"[TIMEOUT] Agente excedeu {timeout}s"
        log.error(output)
    except FileNotFoundError:
        output = "[ERRO] kiro-cli não encontrado no PATH"
        log.error(output)

    # Salvar log do agente
    log_path = _agent_log_path(task)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(output, encoding="utf-8")

    # Extrair e logar credits
    credits_info = _parse_credits(output)
    if credits_info:
        log.info("Agente '%s' #%s — Credits: %s • Time: %s",
                 agent_name, task["id"], credits_info["credits"], credits_info["time"])
    else:
        log.info("Agente '%s' #%s — execução concluída (credits não capturados)", agent_name, task["id"])
