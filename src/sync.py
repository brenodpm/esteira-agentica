"""Sincronização: pipe.yml → disco → GitHub Projects V2."""

import json
from pathlib import Path

from src.github import push_boards, GitHubError, RateLimitError
from src.log import log

BOARDS_DIR = Path(".pipe/boards")
PIPE_DIR = Path(".pipe")
SNAPSHOT_FILE = PIPE_DIR / "snapshot.json"
PIPE_FILE = Path("pipe.yml")


def _load_snapshot() -> dict:
    if SNAPSHOT_FILE.exists():
        return json.loads(SNAPSHOT_FILE.read_text())
    return {}


def _save_snapshot(state: dict) -> None:
    PIPE_DIR.mkdir(exist_ok=True)
    SNAPSHOT_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def _pipe_mtime() -> str:
    return str(PIPE_FILE.stat().st_mtime)


def _desired_from_config(config: dict) -> dict[str, list[str]]:
    return {
        board_id: list(board["columns"].keys())
        for board_id, board in config["boards"].items()
    }


def _ensure_local_dirs(desired: dict[str, list[str]]) -> None:
    BOARDS_DIR.mkdir(parents=True, exist_ok=True)
    for board_id, columns in desired.items():
        board_path = BOARDS_DIR / board_id
        board_path.mkdir(exist_ok=True)
        for col_id in columns:
            (board_path / col_id).mkdir(exist_ok=True)


def _remove_stale_local(desired: dict[str, list[str]]) -> None:
    if not BOARDS_DIR.exists():
        return
    desired_boards = set(desired.keys())
    for board_path in BOARDS_DIR.iterdir():
        if not board_path.is_dir():
            continue
        if board_path.name not in desired_boards:
            _rmdir(board_path)
            continue
        desired_cols = set(desired[board_path.name])
        for col_path in board_path.iterdir():
            if col_path.is_dir() and col_path.name not in desired_cols:
                _rmdir(col_path)


def _rmdir(path: Path) -> None:
    for child in path.iterdir():
        if child.is_dir():
            _rmdir(child)
        else:
            child.unlink()
    path.rmdir()


def _sync_github(config: dict, desired: dict[str, list[str]]) -> None:
    desired_names = {}
    for board_id, col_ids in desired.items():
        cols = config["boards"][board_id]["columns"]
        desired_names[board_id] = [cols[c].get("name", c) for c in col_ids]
    try:
        push_boards(config, desired_names)
    except RateLimitError:
        log.warning("Rate limit — push de boards adiado")
    except GitHubError as e:
        log.error("Erro GitHub (boards): %s", e)


def sync(config: dict) -> None:
    """Sincroniza estrutura. Prioridade: pipe.yml → disco → GitHub."""
    snapshot = _load_snapshot()
    mtime = _pipe_mtime()

    desired = _desired_from_config(config)

    if snapshot.get("pipe_mtime") != mtime:
        # pipe.yml mudou — disco deve refletir exatamente o pipe
        _remove_stale_local(desired)
        _ensure_local_dirs(desired)
        _sync_github(config, desired)
        _save_snapshot({"pipe_mtime": mtime, "boards": desired})
        log.info("Sync concluído (pipe.yml atualizado)")
    elif not BOARDS_DIR.exists():
        # primeira execução sem snapshot
        _ensure_local_dirs(desired)
        _sync_github(config, desired)
        _save_snapshot({"pipe_mtime": mtime, "boards": desired})
        log.info("Sync concluído (inicialização)")
    else:
        log.info("Sync: pipe.yml sem alterações")
