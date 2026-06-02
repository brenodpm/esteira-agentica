import yaml
from pathlib import Path


def load(path: "str | Path" = "esteira.yml") -> dict:
    """Carrega configuração a partir de esteira.yml.

    Campos obrigatórios: git.repo, doc, boards (ao menos um board).
    Retorna dict normalizado com defaults aplicados.
    """
    raw = yaml.safe_load(Path(path).read_text()) or {}

    git = raw.get("git") or {}
    repo = git.get("repo", "").strip()
    if not repo:
        raise ValueError("Campo obrigatório 'git.repo' ausente ou vazio em esteira.yml")

    doc = (raw.get("doc") or "").strip()
    if not doc:
        raise ValueError("Campo obrigatório 'doc' ausente ou vazio em esteira.yml")

    boards = raw.get("boards") or {}
    if not boards:
        raise ValueError("Campo obrigatório 'boards' ausente ou vazio em esteira.yml")

    # Normaliza priority de cada board (default 0) e valida advance
    for board_id, board in boards.items():
        board.setdefault("priority", 0)
        for col_id, col in board.get("columns", {}).items():
            change = col.get("change")
            if change is not None and "advance" not in change:
                raise ValueError(
                    f"Coluna '{col_id}' do board '{board_id}' define 'change' sem 'advance' obrigatório"
                )

    # Normaliza gitflow
    flow = git.get("flow") or {}
    base = flow.get("base", "main")

    # Normaliza pipe (configurações do agente)
    pipe = raw.get("pipe") or {}
    agent_cfg = pipe.get("agent") or {}

    return {
        "repo": repo,
        "doc": doc,
        "boards": boards,
        "gitflow": {
            "branch_base": base,
            "flow": {k: v for k, v in flow.items() if k != "base"},
        },
        "pipe": {
            "timeout": agent_cfg.get("timeout"),
            "sleeptime": agent_cfg.get("sleeptime"),
        },
        "_raw": raw,
    }
