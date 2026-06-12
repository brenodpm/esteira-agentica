"""Seleção de tarefa elegível por ciclo."""

import json
from pathlib import Path

from src.log import log

SNAPSHOT_FILE = Path(".pipe/snapshot.json")
BOARDS_DIR = Path(".pipe/boards")

# Sentinela: issue foi movida de todo, precisa de mais um ciclo de sync
TODO_ADVANCE = "TODO_ADVANCE"


def _advance_from_todo(issue: dict, board_id: str, board: dict) -> bool:
    """Se issue está na coluna 'todo', move para 'advance' localmente.

    Retorna True se houve movimentação (issue precisa de sync antes de rodar agente).
    """
    todo_col = board.get("todo")
    if not todo_col or issue["column"] != todo_col:
        return False

    advance_col = board["columns"][todo_col].get("change", {}).get("advance")
    if not advance_col:
        return False

    # Move arquivos localmente
    new_col_path = BOARDS_DIR / board_id / advance_col
    new_col_path.mkdir(parents=True, exist_ok=True)

    for key in ("path", "history_path", "write_path"):
        old = Path(issue[key])
        new = new_col_path / old.name
        if old.exists():
            old.rename(new)
        issue[key] = str(new)

    issue["column"] = advance_col
    issue["status"] = "l-mv"

    # Persiste no snapshot
    snapshot = json.loads(SNAPSHOT_FILE.read_text())
    for i in snapshot.get("issues", {}).get(board_id, []):
        if i["id"] == issue["id"]:
            i.update(issue)
            break
    SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))

    log.info("[%s] auto-advance #%s: %s → %s", board_id, issue["id"], todo_col, advance_col)
    return True


def pick_task(config: dict) -> dict | str | None:
    """Retorna a primeira issue elegível, TODO_ADVANCE se houve auto-advance, ou None.

    Critérios:
    - Boards ordenados por prioridade (menor = mais prioritário)
    - Issues ordenadas por created_at (mais antiga primeiro)
    - Se issue está em 'todo', faz auto-advance local e retorna TODO_ADVANCE
      (próximo ciclo de sync propaga pro GitHub, depois o agente roda)
    - Elegível se:
      1. status == 'ok'
      2. coluna tem 'agent' definido
      3. coluna tem 'change' com 'advance'
    """
    snapshot = json.loads(SNAPSHOT_FILE.read_text()) if SNAPSHOT_FILE.exists() else {}
    issues_map = snapshot.get("issues", {})

    boards_sorted = sorted(
        config["boards"].items(),
        key=lambda x: x[1].get("priority", 999),
    )

    for board_id, board in boards_sorted:
        issues = issues_map.get(board_id, [])
        candidates = [i for i in issues if i["status"] == "ok" and i.get("id")]
        candidates.sort(key=lambda i: i.get("created_at") or "")

        columns = board["columns"]
        for issue in candidates:
            if _advance_from_todo(issue, board_id, board):
                return TODO_ADVANCE

            col = columns.get(issue["column"], {})
            if not col.get("agent"):
                continue
            change = col.get("change", {})
            if not change.get("advance"):
                continue
            return {"board_id": board_id, **issue}

    return None
