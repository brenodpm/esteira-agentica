import sys
import yaml
from pathlib import Path


def _validate_config(data: dict) -> None:
    """Valida unicidade de campos no pipe.yml. Aborta se encontrar duplicatas."""
    errors = []
    raw_boards = data.get("boards", {})
    boards = {k: v for k, v in raw_boards.items() if isinstance(v, dict) and "columns" in v}

    board_names = {}
    for board_id, board in boards.items():
        # Board names únicos
        name = board.get("name", board_id)
        if name in board_names:
            errors.append(f"boards: name '{name}' duplicado em '{board_id}' e '{board_names[name]}'")
        board_names[name] = board_id

        # Column names únicos dentro de cada board
        col_names = {}
        for col_id, col in board.get("columns", {}).items():
            col_name = col.get("name", col_id) if isinstance(col, dict) else col_id
            if col_name in col_names:
                errors.append(f"boards.{board_id}.columns: name '{col_name}' duplicado em '{col_id}' e '{col_names[col_name]}'")
            col_names[col_name] = col_id

    # Flow prefixes únicos
    flows = data.get("git", {}).get("flow", {})
    prefixes = {}
    for flow_id, flow in flows.items():
        if not isinstance(flow, dict) or "prefix" not in flow:
            continue
        prefix = flow["prefix"]
        if prefix in prefixes:
            errors.append(f"git.flow: prefix '{prefix}' duplicado em '{flow_id}' e '{prefixes[prefix]}'")
        prefixes[prefix] = flow_id

    # Effort levels únicos (keys do dict, YAML já garante, mas model+effort combo)
    # Boards meta: bugs e needs devem referenciar boards existentes
    meta_bugs = raw_boards.get("bugs")
    meta_needs = raw_boards.get("needs")
    if meta_bugs and meta_bugs not in boards:
        errors.append(f"boards.bugs: referencia board '{meta_bugs}' que não existe")
    if meta_needs and meta_needs not in boards:
        errors.append(f"boards.needs: referencia board '{meta_needs}' que não existe")

    if errors:
        msg = "ERRO pipe.yml — duplicatas encontradas:\n  " + "\n  ".join(errors)
        print(msg, file=sys.stderr)
        from src.log import log
        log.error("[Config]" + msg)
        sys.exit(1)


def load_config(path: str) -> dict:
    data = yaml.safe_load(Path(path).read_text())
    _validate_config(data)
    raw_boards = data.get("boards", {})
    boards = {k: v for k, v in raw_boards.items() if isinstance(v, dict) and "columns" in v}
    meta = {k: v for k, v in raw_boards.items() if k not in boards}
    meta.setdefault("alter-remote-boards", False)
    meta.setdefault("allow-del-remote-issue", False)
    return {
        "repo": data["git"]["repo"],
        "boards": boards,
        "boards_meta": meta,
        "pipe": data.get("pipe", {}),
        "git": data.get("git", {}),
        "effort": data.get("effort", {}),
        "ttl-log": data.get("ttl-log", 10),
    }
