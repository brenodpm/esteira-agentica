"""Sincronização de issues entre GitHub Projects e disco local."""

import json
import re
import unicodedata
from pathlib import Path

from src.github import fetch_board_items, fetch_issue_comments, fetch_updated_issues, GitHubError, RateLimitError

PIPE_DIR = Path(".pipe")
BOARDS_DIR = PIPE_DIR / "boards"
SNAPSHOT_FILE = PIPE_DIR / "snapshot.json"


def _load_snapshot() -> dict:
    if SNAPSHOT_FILE.exists():
        return json.loads(SNAPSHOT_FILE.read_text())
    return {}


def _save_snapshot(snapshot: dict) -> None:
    SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def _sanitize_name(text: str) -> str:
    return text.replace(".", "").replace("-", "")


def _col_name_to_id(config: dict, board_id: str) -> dict[str, str]:
    return {
        col.get("name", col_id): col_id
        for col_id, col in config["boards"][board_id]["columns"].items()
    }


def _build_history(repo: str, issue_number: int) -> tuple[str, str]:
    try:
        data = fetch_issue_comments(repo, issue_number)
    except GitHubError:
        return "", ""
    updated_at = data.get("updatedAt", "")
    comments = data.get("comments", [])
    if not comments:
        return "", updated_at
    lines = []
    for c in comments:
        lines.append(f"{c['author']['login']} - {c['createdAt']}")
        lines.append(c["body"])
        lines.append("--------")
        lines.append("")
    return "\n".join(lines), updated_at


def sync_issues(config: dict) -> None:
    """Busca issues do GitHub e registra novas no snapshot com status b-new."""
    snapshot = _load_snapshot()
    if "issues" not in snapshot:
        snapshot["issues"] = {}

    repo = config["repo"]
    last_sync = snapshot.get("last_sync")

    # Se já temos um sync anterior, busca só issues modificadas desde então
    try:
        if last_sync:
            updated_numbers = set(fetch_updated_issues(repo, last_sync))
            if not updated_numbers:
                return
        else:
            updated_numbers = None

        remote_items = fetch_board_items(config)
    except RateLimitError:
        print("  ⚠ Rate limit — sync de issues adiado.")
        return
    except GitHubError as e:
        print(f"  ⚠ Erro GitHub (issues): {e}")
        return

    for board_id, items in remote_items.items():
        name_to_id = _col_name_to_id(config, board_id)
        if board_id not in snapshot["issues"]:
            snapshot["issues"][board_id] = []

        for item in items:
            if updated_numbers is not None and item["number"] not in updated_numbers:
                continue

            col_id = name_to_id.get(item["status"])
            if not col_id:
                continue

            if _issue_exists_in_snapshot(snapshot, board_id, item["number"]):
                continue

            slug = _slugify(item["title"])
            base = f"{item['number']}-{slug}"
            col_path = BOARDS_DIR / board_id / col_id

            entry = {
                "id": item["number"],
                "name": _sanitize_name(item["title"]),
                "column": col_id,
                "path": str(col_path / f"{base}.md"),
                "history_path": str(col_path / f"{base}-history.md"),
                "write_path": str(col_path / f"{base}-write.md"),
                "l-time": None,
                "b-time": None,
                "status": "b-new",
            }

            snapshot["issues"][board_id].append(entry)

    _create_local_files(snapshot, config, remote_items)

    from datetime import datetime, timezone
    snapshot["last_sync"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    _save_snapshot(snapshot)


def _issue_exists_in_snapshot(snapshot: dict, board_id: str, number: int) -> bool:
    for issue in snapshot.get("issues", {}).get(board_id, []):
        if issue["id"] == number:
            return True
    return False


def _create_local_files(snapshot: dict, config: dict, remote_items: dict) -> None:
    items_by_board = {}
    for board_id, items in remote_items.items():
        for item in items:
            items_by_board[(board_id, item["number"])] = item

    repo = config["repo"]

    for board_id, issues in snapshot.get("issues", {}).items():
        for issue in issues:
            if issue["status"] != "b-new":
                continue

            filepath = Path(issue["path"])
            history_path = Path(issue["history_path"])
            write_path = Path(issue["write_path"])
            filepath.parent.mkdir(parents=True, exist_ok=True)

            item = items_by_board.get((board_id, issue["id"]))
            body = item["body"] if item else ""
            filepath.write_text(f"# {issue['name']}\n\n{body}\n")

            history, updated_at = _build_history(repo, issue["id"])
            history_path.write_text(history)

            write_path.write_text("")

            issue["l-time"] = str(filepath.stat().st_mtime)
            issue["b-time"] = updated_at
            issue["status"] = "ok"
