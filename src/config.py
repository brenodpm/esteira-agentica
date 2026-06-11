import yaml
from pathlib import Path


def load_config(path: str) -> dict:
    data = yaml.safe_load(Path(path).read_text())
    return {
        "repo": data["git"]["repo"],
        "boards": data.get("boards", {}),
        "pipe": data.get("pipe", {}),
        "git": data.get("git", {}),
    }
