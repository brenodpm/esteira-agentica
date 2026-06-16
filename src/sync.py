"""Sincronização: pipe.yml → disco → GitHub Projects V2."""

import json
from datetime import datetime, timezone
from pathlib import Path

from src.github import (
    push_boards, resolve_project_metadata, fetch_board_items_graphql,
    GitHubError, RateLimitError,
)
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
    """Cria/atualiza boards remotos (somente se create-remote-boards=true)."""
    if not config["boards_meta"].get("create-remote-boards"):
        log.debug("[sync_github] create-remote-boards=false — pulando")
        return
    log.info("[sync_github] create-remote-boards=true — sincronizando boards remotos")
    desired_names = {}
    for board_id, col_ids in desired.items():
        cols = config["boards"][board_id]["columns"]
        desired_names[board_id] = [cols[c].get("name", c) for c in col_ids]
    log.debug("[sync_github] Desired names: %s", {k: v for k, v in desired_names.items()})
    try:
        push_boards(config, desired_names)
    except RateLimitError:
        log.warning("Rate limit — push de boards adiado")
    except GitHubError as e:
        log.error("Erro GitHub (boards): %s", e)


def _populate_cache(config: dict, cache: dict) -> None:
    """Resolve metadata de cada board e popula o cache."""
    for board_id in config["boards"]:
        try:
            resolve_project_metadata(config, board_id, cache)
        except GitHubError as e:
            log.warning("Cache: board '%s' não resolvido: %s", board_id, e)


def sync(config: dict) -> dict:
    """Sincronização inicial. Retorna snapshot atualizado."""
    log.info("Sync iniciado...")

    snapshot = _load_snapshot()
    mtime = _pipe_mtime()
    desired = _desired_from_config(config)

    if not snapshot:
        # Fluxo sem snapshot — criação do projeto
        _ensure_local_dirs(desired)
        _sync_github(config, desired)
        cache = {}
        _populate_cache(config, cache)
        now = datetime.now(timezone.utc).isoformat()
        snapshot = {
            "pipe_mtime": mtime,
            "boards": desired,
            "cache": cache,
            "issues": {bid: [] for bid in desired},
            "last_sync": now,
        }
        _save_snapshot(snapshot)
        log.info("Sync concluído (inicialização)")
    elif snapshot.get("pipe_mtime") != mtime:
        # Fluxo com snapshot — pipe.yml mudou
        _remove_stale_local(desired)
        _ensure_local_dirs(desired)
        _sync_github(config, desired)
        now = datetime.now(timezone.utc).isoformat()
        snapshot["pipe_mtime"] = mtime
        snapshot["boards"] = desired
        snapshot["last_sync"] = now
        snapshot.setdefault("cache", {})
        snapshot.setdefault("issues", {})
        _populate_cache(config, snapshot["cache"])
        _save_snapshot(snapshot)
        log.info("Sync concluído (pipe.yml atualizado)")
    else:
        log.info("Sync: pipe.yml sem alterações")

    return snapshot


def should_full_sync(snapshot: dict) -> bool:
    """Retorna True se last_sync é do dia anterior ou mais antigo (virada de dia)."""
    last_sync = snapshot.get("last_sync")
    if not last_sync:
        return True
    try:
        last_dt = datetime.fromisoformat(last_sync.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return last_dt.date() < now.date()
    except (ValueError, AttributeError):
        return True


def full_sync(config: dict, snapshot: dict) -> None:
    """Sincronização por virada de dia: atualiza boards, busca items, marca b-new/b-del."""
    desired = _desired_from_config(config)

    # Atualizar boards remotos se create-remote-boards=true
    _sync_github(config, desired)

    cache = snapshot.setdefault("cache", {})

    # Buscar lista completa de items de cada board
    for board_id in config["boards"]:
        try:
            meta = resolve_project_metadata(config, board_id, cache)
        except GitHubError as e:
            log.warning("full_sync: board '%s' não resolvido: %s", board_id, e)
            continue

        remote_items = fetch_board_items_graphql(meta["project_id"])

        # Atualizar cache de items
        items_cache = meta.setdefault("items", {})
        for item in remote_items:
            items_cache[str(item["number"])] = item["item_id"]

        remote_numbers = {item["number"] for item in remote_items}
        issues = snapshot.setdefault("issues", {}).setdefault(board_id, [])
        snapshot_numbers = {i["id"] for i in issues}

        # Issues no GitHub mas não no snapshot → b-new
        for item in remote_items:
            if item["number"] not in snapshot_numbers:
                issues.append({
                    "id": item["number"],
                    "name": item["title"],
                    "column": item["status"],
                    "path": None,
                    "history_path": None,
                    "write_path": None,
                    "l-time": None,
                    "b-time": item["updated_at"],
                    "created_at": None,
                    "status": "b-new",
                })

        # Issues no snapshot mas não no GitHub → b-del
        for issue in issues:
            if issue["id"] not in remote_numbers and issue["status"] == "ok":
                issue["status"] = "b-del"

    # Atualizar last_sync
    snapshot["last_sync"] = datetime.now(timezone.utc).isoformat()
    _save_snapshot(snapshot)
    log.info("Full sync (virada de dia) concluído")
