import json
from pathlib import Path

_DEFAULT_GITFLOW = {
    "branch_base": "develop",
    "prefixes": {
        "feature": "feature/",
        "fix": "fix/",
        "release": "release/",
        "hotfix": "hotfix/",
    },
}

_DEFAULT_BOARD = {
    "columns": ["Backlog", "In Progress", "Done"],
    "labels": {},
}

_DEFAULT_AGENTS_SEQUENCE = [
    "requirements",
    "architecture",
    "engineering",
    "quality",
]


def load(path: "str | Path" = "config/project.json") -> dict:
    data = json.loads(Path(path).read_text())

    if not data.get("repo"):
        raise ValueError("Campo obrigatório 'repo' ausente ou vazio em config")

    gitflow = data.get("gitflow", {})
    gitflow.setdefault("branch_base", _DEFAULT_GITFLOW["branch_base"])
    gitflow.setdefault("prefixes", _DEFAULT_GITFLOW["prefixes"])
    data["gitflow"] = gitflow

    board = data.get("board", {})
    board.setdefault("columns", _DEFAULT_BOARD["columns"])
    board.setdefault("labels", _DEFAULT_BOARD["labels"])
    data["board"] = board

    data.setdefault("agents_sequence", _DEFAULT_AGENTS_SEQUENCE)

    return data
