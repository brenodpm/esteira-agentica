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


def _is_fixed_branch(name: str, flow: dict) -> bool:
    """Retorna True se o nome é uma branch fixa (não é prefixo de outro flow)."""
    prefixes = {f["prefix"] for f in flow.values() if isinstance(f, dict) and "prefix" in f}
    return name not in prefixes


def _read_branch_from_issue(task_path: str) -> str | None:
    """Extrai branch da issue via <!-- branch: X --> ou label branch:X."""
    p = Path(task_path)
    if not p.exists():
        return None
    content = p.read_text()
    # <!-- branch: release/v1.0 -->
    m = re.search(r"<!--\s*branch:\s*(.+?)\s*-->", content)
    if m:
        return m.group(1).strip()
    # /branch release/v1.0 ou label branch:release/v1.0
    m = re.search(r"(?:^|\s)/branch\s+(\S+)", content)
    if m:
        return m.group(1).strip()
    m = re.search(r"branch:(\S+)", content)
    if m:
        return m.group(1).strip()
    return None


def _resolve_target_branch(config: dict, board: dict, task: dict, direction: str) -> str | None:
    """Resolve a branch de create ou merge.
    
    Retorna o nome exato da branch se possível, ou None se não conseguir resolver.
    direction: 'create' ou 'merge'
    """
    flow_type = board.get("flow", "feature")
    flow = config["git"]["flow"]
    target = flow[flow_type].get(direction, flow.get("base", "main"))

    if _is_fixed_branch(target, flow):
        return target

    # É um prefixo — tentar resolver da issue
    branch_from_issue = _read_branch_from_issue(task["path"])
    if branch_from_issue and branch_from_issue.startswith(target):
        return branch_from_issue

    return None


def _resolve_origin_branch(config: dict, board: dict, task: dict) -> str | None:
    return _resolve_target_branch(config, board, task, "create")


def _resolve_merge_branch(config: dict, board: dict, task: dict) -> str | None:
    return _resolve_target_branch(config, board, task, "merge")


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
    origin_branch = _resolve_origin_branch(config, board, task)
    merge_branch = _resolve_merge_branch(config, board, task)
    base_branch = config["git"]["flow"].get("base", "main")

    flow_type = board.get("flow", "feature")
    flow = config["git"]["flow"]
    origin_prefix = flow[flow_type].get("create", flow.get("base", "main"))
    merge_prefix = flow[flow_type].get("merge", flow.get("base", "main"))

    create_branch = "create" in gitevents
    do_merge = "merge" in gitevents

    needs_board = config.get("boards_meta", {}).get("needs", "debito")
    needs_dir = str(BOARDS_DIR / needs_board / "backlog")

    lines = []

    lines.append(f"Etapa: {column.get('name', task['column'])}")
    lines.append(f"Tarefa: {task['name']}")
    if column.get("acao"):
        lines.append(f"Descrição: {column['acao']}")
    lines.append("")

    # --- GIT SETUP ---
    lines.append("## 1. Git setup (execute via shell)")
    lines.append("```bash")
    lines.append("git fetch origin")
    if create_branch:
        if origin_branch:
            lines.append(f"git checkout {origin_branch} && git pull origin {origin_branch}")
        else:
            lines.append(f"# branch de origem é um prefixo '{origin_prefix}' — descubra a branch exata:")
            lines.append(f"# procure no body da issue em `{task['path']}` por <!-- branch: {origin_prefix}/... -->")
            lines.append(f"# ou use: git branch -r | grep 'origin/{origin_prefix}/' | head -1")
            lines.append(f"# então: git checkout <branch_encontrada> && git pull origin <branch_encontrada>")
        lines.append(f"git checkout -b {branch_name}")
    else:
        lines.append(f"git checkout {branch_name} 2>/dev/null || git checkout -b {branch_name} origin/{branch_name}")
        lines.append(f"git pull origin {branch_name} 2>/dev/null || true")
    lines.append("```")
    lines.append("")

    # --- EXECUÇÃO DA TAREFA ---
    lines.append("## 2. Executar tarefa")
    lines.append(f"- Leia a issue em `{task['path']}` e o histórico em `{task['history_path']}` para checar se há orientações extras e execute o que é pedidi")
    lines.append(f"- Verifique se as tarefas em `/blocked_by` foram concluídas; se NÃO: anote em `{task['write_path']}` e vá direto para o passo de cleanup")
    lines.append(f"- Se houver dúvidas: escreva em `{task['write_path']}` e adicione `/need_human` no body da issue, depois vá para cleanup")
    lines.append(f"- Se a execução depender da conclusão de outra demanda adicione `/blocked_by` no body seguida pelo id e board da demanda, depois vá para cleanup")
    lines.append(f"- Se necessitar de alguma definição|documentação|especificação que seja bloqueante: crie um card em `{needs_dir}` solicitando tudo que precisa (verificar antes se a demanda não existe), depois vá para cleanup")
    lines.append(f"- Ao criar novos cards em `.pipe/boards/`, nomeie SEM prefixo numérico (ex: `minha-tarefa.md`, NÃO `1-minha-tarefa.md`). A esteira atribui o ID automaticamente.")
    lines.append("")

    # --- COMMIT & PUSH ---
    lines.append("## 3. Commit e push (execute via shell)")
    lines.append("```bash")
    lines.append("git add -A -- ':!.pipe'")
    lines.append("# NUNCA versione o diretório .pipe/ — ele é gerenciado pela esteira")
    lines.append(f'git commit -m "{column.get("name", task["column"])}: {task["name"]}"')
    lines.append(f"git push -u origin {branch_name}")
    lines.append("```")
    lines.append("")

    # --- MERGE ---
    if do_merge:
        lines.append("## 4. Pull Request (execute via shell)")
        if merge_branch:
            lines.append("```bash")
            lines.append(f"git push origin {branch_name}")
            lines.append(f"gh pr create --base {merge_branch} --head {branch_name} --title \"merge: {branch_name} -> {merge_branch}\" --body \"Automated PR from agent\"")
            lines.append("```")
        else:
            lines.append(f"A branch de merge usa prefixo '{merge_prefix}'. Descubra a branch exata:")
            lines.append(f"- Procure no body da issue `{task['path']}` por `<!-- branch: {merge_prefix}/... -->`")
            lines.append(f"- Ou use: `git branch -r | grep 'origin/{merge_prefix}/'` para encontrar")
            lines.append("```bash")
            lines.append(f"git push origin {branch_name}")
            lines.append("# substitua <MERGE_BRANCH> pela branch correta encontrada:")
            lines.append(f"gh pr create --base <MERGE_BRANCH> --head {branch_name} --title \"merge: {branch_name} -> <MERGE_BRANCH>\" --body \"Automated PR from agent\"")
            lines.append("```")
        lines.append("")

    # --- RESUMO ---
    step = 5 if do_merge else 4
    lines.append(f"## {step}. Resumo")
    lines.append(f"- Anote um resumo curto do que foi executado em `{task['write_path']}`")
    lines.append("")

    # --- CLEANUP ---
    step += 1
    lines.append(f"## {step}. Cleanup (execute via shell)")
    lines.append("```bash")
    lines.append(f"git checkout {base_branch}")
    lines.append(f"git branch -D {branch_name} 2>/dev/null || true")
    lines.append("```")
    lines.append("")

    # --- TRANSIÇÕES ---
    lines.append("## Transição de coluna (OBRIGATÓRIO)")
    lines.append("Ao finalizar, você DEVE mover os 3 arquivos da issue (`.md`, `-history.md`, `-write.md`) para a coluna de destino.")
    lines.append("Se não mover, a esteira vai re-executar esta mesma tarefa no próximo ciclo.")
    lines.append("")
    change = column.get("change", {})
    for condition, target_col in change.items():
        target_dir = str(BOARDS_DIR / board_id / target_col)
        lines.append(f"- **{condition}** → `mv {task['path']} {task['history_path']} {task['write_path']} {target_dir}/`")

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
    clean_output = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]|\x1b\].*?\x07|\x1b\[.*?[A-Za-z]", "", output)
    log_path.write_text(f"═══ PROMPT ═══\n{prompt}\n\n═══ OUTPUT ═══\n{clean_output}\n", encoding="utf-8")

    # Extrair e logar credits
    credits_info = _parse_credits(output)
    if credits_info:
        log.info("Agente '%s' #%s — Credits: %s • Time: %s",
                 agent_name, task["id"], credits_info["credits"], credits_info["time"])
    else:
        log.info("Agente '%s' #%s — execução concluída (credits não capturados)", agent_name, task["id"])
