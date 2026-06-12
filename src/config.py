import yaml
from pathlib import Path


def load_config(path: str) -> dict:
    data = yaml.safe_load(Path(path).read_text())
    raw_boards = data.get("boards", {})
    boards = {k: v for k, v in raw_boards.items() if isinstance(v, dict) and "columns" in v}
    return {
        "repo": data["git"]["repo"],
        "boards": boards,
        "boards_meta": {k: v for k, v in raw_boards.items() if k not in boards},
        "pipe": data.get("pipe", {}),
        "git": data.get("git", {}),
    }
