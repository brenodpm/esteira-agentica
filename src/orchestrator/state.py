import json
import os
from pathlib import Path

_INITIAL_STATE = {
    "current_feature": None,
    "current_step": None,
    "status": "idle",
    "issue_number": None,
}


def load(path: str | Path = "state.json") -> dict:
    p = Path(path)
    if not p.exists():
        return dict(_INITIAL_STATE)
    return json.loads(p.read_text())


def save(state: dict, path: str | Path = "state.json") -> None:
    p = Path(path)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(state))
    os.replace(tmp, p)
