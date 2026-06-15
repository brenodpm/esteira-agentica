import yaml
from pathlib import Path


def load_config(path: str) -> dict:
    data = yaml.safe_load(Path(path).read_text())
    raw_boards = data.get("boards", {})
    boards = {k: v for k, v in raw_boards.items() if isinstance(v, dict) and "columns" in v}
    meta = {k: v for k, v in raw_boards.items() if k not in boards}
    meta.setdefault("create-remote-boards", False)
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
