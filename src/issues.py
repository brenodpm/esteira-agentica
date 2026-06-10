"""Sincronização de issues entre GitHub Projects e disco local."""

import json
import re
import unicodedata
from datetime import datetime, timezone, timedelta
from pathlib import Path

from src.github import (
    fetch_board_items, fetch_issue_comments, fetch_updated_issues,
    GitHubError, RateLimitError,
)
from src.log import log

PIPE_DIR = Path(".pipe")
BOARDS_DIR = PIPE_DIR / "boards"
SNAPSHOT_FILE = PIPE_DIR / "snapshot.json"


def _load_snapshot() -> dict:
    if SNAPSHOT_FILE.exists():
        return json.loads(SNAPSHOT_FILE.read_text())
    return {}


def _save_snapshot(snapshot: dict) -> None:
    SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def _find_file_in_boards(board_id: str, issue_id: int) -> Path | None:
    """Procura o arquivo slug de uma issue em qualquer coluna do board."""
    board_path = BOARDS_DIR / board_id
    if not board_path.exists():
        return None
    prefix = f"{issue_id}-"
    for col_dir in board_path.iterdir():
        if not col_dir.is_dir():
            continue
        for f in col_dir.iterdir():
            if f.name.startswith(prefix) and not f.name.endswith(("-history.md", "-write.md")):
                return f
    return None


def _scan_local_files(board_id: str) -> dict[int, Path]:
    """Retorna {issue_id: path} de todos os arquivos slug no board."""
    board_path = BOARDS_DIR / board_id
    result = {}
    if not board_path.exists():
        return result
    for col_dir in board_path.iterdir():
        if not col_dir.is_dir():
            continue
        for f in col_dir.iterdir():
            if f.is_file() and not f.name.endswith(("-history.md", "-write.md")) and f.suffix == ".md":
                match = re.match(r"^(\d+)-", f.name)
                if match:
                    result[int(match.group(1))] = f
    return result


def _col_from_path(path: Path) -> str:
    """Extrai col_id do path: .pipe/boards/<board>/<col>/file.md"""
    return path.parent.name


def _handle_orphan_files(issue: dict, new_col_path: Path, repo: str) -> None:
    """Limpa history/write órfãos no diretório anterior quando slug foi movido."""
    old_history = Path(issue["history_path"])
    old_write = Path(issue["write_path"])

    # Se history ficou no dir anterior, remove
    if old_history.exists() and old_history.parent != new_col_path:
        old_history.unlink()

    # Se write ficou no dir anterior, posta conteúdo e remove
    if old_write.exists() and old_write.parent != new_col_path:
        content = old_write.read_text().strip()
        if content:
            log.info("Write órfão issue #%s — pendente postar comentário", issue['id'])
        old_write.unlink()


def _should_full_sync(last_sync: str | None) -> bool:
    """Retorna True se last_sync é do dia anterior ou mais antigo."""
    if not last_sync:
        return True
    try:
        last_dt = datetime.fromisoformat(last_sync.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return last_dt.date() < now.date()
    except (ValueError, AttributeError):
        return True


def sync_issues(config: dict) -> None:
    """Loop principal de sincronização de issues."""
    snapshot = _load_snapshot()
    if "issues" not in snapshot:
        snapshot["issues"] = {}

    repo = config["repo"]
    last_sync = snapshot.get("last_sync")

    # Determina se precisa full sync
    full_sync = _should_full_sync(last_sync)

    try:
        if full_sync:
            updated_numbers = None
        else:
            updated_numbers = set(fetch_updated_issues(repo, last_sync))
            if not updated_numbers:
                # Ainda precisa checar mudanças locais
                _detect_local_changes(snapshot, config)
                _save_snapshot(snapshot)
                return

        remote_items = fetch_board_items(config)
    except RateLimitError:
        log.warning("Rate limit — sync de issues adiado")
        return
    except GitHubError as e:
        log.error("Erro GitHub (issues): %s", e)
        return

    # Indexar remote por board_id -> {number: item}
    remote_by_board = {}
    for board_id, items in remote_items.items():
        name_to_id = _col_name_to_id(config, board_id)
        remote_by_board[board_id] = {}
        for item in items:
            col_id = name_to_id.get(item["status"])
            if col_id:
                remote_by_board[board_id][item["number"]] = {**item, "col_id": col_id}

    # === DETECÇÃO DE MUDANÇAS ===
    for board_id in list(config["boards"].keys()):
        if board_id not in snapshot["issues"]:
            snapshot["issues"][board_id] = []

        issues = snapshot["issues"][board_id]
        remote = remote_by_board.get(board_id, {})
        local_files = _scan_local_files(board_id)

        # Processar issues existentes no snapshot
        for issue in issues:
            if issue["status"] in ("b-new", "l-new"):
                continue  # será tratado na fase de ações

            number = issue["id"]

            # QUANDO issue no snapshot mas não no board
            if number and number not in remote:
                issue["b-time"] = _now_iso()
                issue["status"] = "b-del"
                continue

            # QUANDO issue no snapshot mas não no diretório
            if number in local_files:
                local_path = local_files[number]
            else:
                local_path = None

            if not local_path and not Path(issue["path"]).exists():
                issue["l-time"] = _now_iso()
                issue["status"] = "l-del"
                continue

            if local_path:
                current_col = _col_from_path(local_path)
                # QUANDO coluna local diferente do snapshot
                if current_col != issue["column"]:
                    new_col_path = local_path.parent
                    _handle_orphan_files(issue, new_col_path, repo)
                    slug = local_path.stem
                    issue["l-time"] = str(local_path.stat().st_mtime)
                    issue["path"] = str(local_path)
                    issue["history_path"] = str(new_col_path / f"{slug}-history.md")
                    issue["write_path"] = str(new_col_path / f"{slug}-write.md")
                    issue["status"] = "l-mv"
                    continue

                # QUANDO mtime do slug ou write > l-time
                file_mtime = str(local_path.stat().st_mtime)
                write_path = Path(issue["write_path"])
                write_mtime = str(write_path.stat().st_mtime) if write_path.exists() else "0"
                latest_mtime = max(file_mtime, write_mtime)

                if issue["l-time"] and latest_mtime > issue["l-time"]:
                    issue["l-time"] = latest_mtime
                    issue["status"] = "l-sync"
                    continue

            # QUANDO b-time do board diferente do snapshot
            if number and number in remote:
                remote_item = remote[number]
                remote_col = remote_item["col_id"]

                # QUANDO coluna no board diferente do snapshot (b-mv)
                if issue["status"] == "ok" and remote_col != issue["column"]:
                    issue["column"] = remote_col
                    issue["b-time"] = _now_iso()
                    issue["status"] = "b-mv"
                    continue

            # Checagem de b-time precisa do updatedAt (caro, só se updated_numbers indica)
            if updated_numbers and number in updated_numbers:
                issue["status"] = "b-sync"
                issue["b-time"] = _now_iso()

        # QUANDO arquivo no diretório mas não no snapshot
        snapshot_ids = {i["id"] for i in issues}
        snapshot_paths = {i["path"] for i in issues}
        for file_id, file_path in local_files.items():
            if file_id in snapshot_ids:
                continue
            if str(file_path) in snapshot_paths:
                continue

            # Se já existe no remote, é reconciliação (não é l-new)
            if file_id in remote:
                remote_item = remote[file_id]
                col_id = _col_from_path(file_path)
                slug = file_path.stem
                status = "ok" if col_id == remote_item["col_id"] else "l-mv"
                entry = {
                    "id": file_id,
                    "name": _sanitize_name(remote_item["title"]),
                    "column": col_id,
                    "path": str(file_path),
                    "history_path": str(file_path.parent / f"{slug}-history.md"),
                    "write_path": str(file_path.parent / f"{slug}-write.md"),
                    "l-time": str(file_path.stat().st_mtime),
                    "b-time": _now_iso(),
                    "status": status,
                }
                issues.append(entry)
                continue

            # Issue nova local (não existe no remote)
            first_line = ""
            try:
                first_line = file_path.read_text().splitlines()[0].lstrip("# ").strip()
            except (IndexError, OSError):
                first_line = file_path.stem

            col_id = _col_from_path(file_path)
            entry = {
                "id": None,
                "name": _sanitize_name(first_line),
                "column": col_id,
                "path": str(file_path),
                "history_path": str(file_path.parent / f"{file_path.stem}-history.md"),
                "write_path": str(file_path.parent / f"{file_path.stem}-write.md"),
                "l-time": str(file_path.stat().st_mtime),
                "b-time": None,
                "status": "l-new",
            }
            issues.append(entry)

        # QUANDO issues novas vindo do board (não estão no snapshot)
        current_ids = {i["id"] for i in issues}
        for number, remote_item in remote.items():
            if number in current_ids:
                continue

            slug = _slugify(remote_item["title"])
            base = f"{number}-{slug}"
            col_path = BOARDS_DIR / board_id / remote_item["col_id"]

            entry = {
                "id": number,
                "name": _sanitize_name(remote_item["title"]),
                "column": remote_item["col_id"],
                "path": str(col_path / f"{base}.md"),
                "history_path": str(col_path / f"{base}-history.md"),
                "write_path": str(col_path / f"{base}-write.md"),
                "l-time": None,
                "b-time": None,
                "status": "b-new",
            }
            issues.append(entry)

    # === AÇÕES POR STATUS ===
    _execute_actions(snapshot, config, remote_by_board)

    # Atualiza last_sync
    if full_sync:
        today_midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        snapshot["last_sync"] = today_midnight.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        snapshot["last_sync"] = _now_iso()

    _save_snapshot(snapshot)


def _detect_local_changes(snapshot: dict, config: dict) -> None:
    """Detecta mudanças locais mesmo sem issues modificadas no board."""
    for board_id in list(config["boards"].keys()):
        if board_id not in snapshot["issues"]:
            snapshot["issues"][board_id] = []

        issues = snapshot["issues"][board_id]
        local_files = _scan_local_files(board_id)

        for issue in issues:
            if issue["status"] != "ok":
                continue

            number = issue["id"]
            local_path = local_files.get(number)

            if not local_path and not Path(issue["path"]).exists():
                issue["l-time"] = _now_iso()
                issue["status"] = "l-del"
                continue

            if local_path:
                current_col = _col_from_path(local_path)
                if current_col != issue["column"]:
                    new_col_path = local_path.parent
                    _handle_orphan_files(issue, new_col_path, "")
                    slug = local_path.stem
                    issue["l-time"] = str(local_path.stat().st_mtime)
                    issue["path"] = str(local_path)
                    issue["history_path"] = str(new_col_path / f"{slug}-history.md")
                    issue["write_path"] = str(new_col_path / f"{slug}-write.md")
                    issue["status"] = "l-mv"
                    continue

                file_mtime = str(local_path.stat().st_mtime)
                write_path = Path(issue["write_path"])
                write_mtime = str(write_path.stat().st_mtime) if write_path.exists() else "0"
                latest_mtime = max(file_mtime, write_mtime)

                if issue["l-time"] and latest_mtime > issue["l-time"]:
                    issue["l-time"] = latest_mtime
                    issue["status"] = "l-sync"

        # Novos arquivos locais
        snapshot_ids = {i["id"] for i in issues}
        snapshot_paths = {i["path"] for i in issues}
        for file_id, file_path in local_files.items():
            if file_id in snapshot_ids:
                continue
            if str(file_path) in snapshot_paths:
                continue
            first_line = ""
            try:
                first_line = file_path.read_text().splitlines()[0].lstrip("# ").strip()
            except (IndexError, OSError):
                first_line = file_path.stem
            col_id = _col_from_path(file_path)
            issues.append({
                "id": None,
                "name": _sanitize_name(first_line),
                "column": col_id,
                "path": str(file_path),
                "history_path": str(file_path.parent / f"{file_path.stem}-history.md"),
                "write_path": str(file_path.parent / f"{file_path.stem}-write.md"),
                "l-time": str(file_path.stat().st_mtime),
                "b-time": None,
                "status": "l-new",
            })


def _execute_actions(snapshot: dict, config: dict, remote_by_board: dict) -> None:
    """Executa ações baseadas no status de cada issue."""
    repo = config["repo"]

    for board_id, issues in list(snapshot.get("issues", {}).items()):
        to_remove = []

        for i, issue in enumerate(issues):
            status = issue["status"]

            if status == "b-new":
                _action_b_new(issue, repo)
                log.info("[%s] b-new #%s %s", board_id, issue["id"], issue["name"])

            elif status == "b-del":
                _action_b_del(issue)
                log.info("[%s] b-del #%s", board_id, issue["id"])
                to_remove.append(i)

            elif status == "b-sync":
                _action_b_sync(issue, repo)

            elif status == "b-mv":
                _action_b_mv(issue, repo)
                log.info("[%s] b-mv #%s → %s", board_id, issue["id"], issue["column"])

            elif status == "l-del":
                _action_l_del(issue, config, board_id)
                log.info("[%s] l-del #%s", board_id, issue["id"])
                to_remove.append(i)

            elif status == "l-mv":
                _action_l_mv(issue, config, board_id)
                log.info("[%s] l-mv #%s → %s", board_id, issue["id"], issue["column"])

            elif status == "l-sync":
                _action_l_sync(issue, repo)

            elif status == "l-new":
                _action_l_new(issue, config, board_id, repo)
                log.info("[%s] l-new #%s %s", board_id, issue["id"], issue["name"])

        # Remove do snapshot
        for idx in reversed(to_remove):
            issues.pop(idx)


def _action_b_new(issue: dict, repo: str) -> None:
    """Cria os 3 arquivos locais para issue vinda do board."""
    filepath = Path(issue["path"])
    history_path = Path(issue["history_path"])
    write_path = Path(issue["write_path"])
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Arquivo principal
    try:
        from src.github import fetch_issue_comments
        data = fetch_issue_comments(repo, issue["id"])
        body = ""
        # Busca body direto da issue
        from subprocess import run
        result = run(["gh", "issue", "view", str(issue["id"]), "--repo", repo,
                      "--json", "body"], capture_output=True, text=True)
        if result.returncode == 0:
            body = json.loads(result.stdout).get("body", "")
        updated_at = data.get("updatedAt", "")
    except Exception:
        body = ""
        updated_at = ""

    filepath.write_text(f"# {issue['name']}\n\n{body}\n")

    # History
    history, hist_updated = _build_history(repo, issue["id"])
    history_path.write_text(history)
    if hist_updated:
        updated_at = hist_updated

    # Write (vazio)
    write_path.write_text("")

    issue["l-time"] = str(filepath.stat().st_mtime)
    issue["b-time"] = updated_at or _now_iso()
    issue["status"] = "ok"


def _action_b_del(issue: dict) -> None:
    """Remove os 3 arquivos locais."""
    for key in ("path", "history_path", "write_path"):
        p = Path(issue[key])
        if p.exists():
            p.unlink()


def _action_b_sync(issue: dict, repo: str) -> None:
    """Atualiza history e principal se body mudou no board."""
    filepath = Path(issue["path"])
    history_path = Path(issue["history_path"])

    # Atualiza history
    history, updated_at = _build_history(repo, issue["id"])
    if history:
        history_path.write_text(history)

    # Atualiza body se mudou
    try:
        from subprocess import run
        result = run(["gh", "issue", "view", str(issue["id"]), "--repo", repo,
                      "--json", "body"], capture_output=True, text=True)
        if result.returncode == 0:
            body = json.loads(result.stdout).get("body", "")
            new_content = f"# {issue['name']}\n\n{body}\n"
            if filepath.exists() and filepath.read_text() != new_content:
                filepath.write_text(new_content)
                issue["l-time"] = str(filepath.stat().st_mtime)
    except Exception:
        pass

    if updated_at:
        issue["b-time"] = updated_at
    issue["status"] = "ok"


def _action_b_mv(issue: dict, repo: str) -> None:
    """Move arquivos locais para nova coluna."""
    old_path = Path(issue["path"])
    board_id = old_path.parent.parent.name
    new_col = issue["column"]
    new_col_path = BOARDS_DIR / board_id / new_col

    new_col_path.mkdir(parents=True, exist_ok=True)

    # Move os 3 arquivos
    for key in ("path", "history_path", "write_path"):
        old = Path(issue[key])
        new = new_col_path / old.name
        if old.exists():
            old.rename(new)
        issue[key] = str(new)

    # Atualiza history no novo local
    history, updated_at = _build_history(repo, issue["id"])
    history_path = Path(issue["history_path"])
    if history:
        history_path.write_text(history)

    if updated_at:
        issue["b-time"] = updated_at
    issue["status"] = "ok"


# ── Ações local → GitHub ──────────────────────────────────────────────────────


def _action_l_new(issue: dict, config: dict, board_id: str, repo: str) -> None:
    """Cria issue no GitHub, apaga arquivo original, recria com padrão correto."""
    from src.github import create_issue, move_card

    filepath = Path(issue["path"])
    body = ""
    if filepath.exists():
        lines = filepath.read_text().splitlines()
        # Pula a primeira linha (# titulo) e linha vazia
        body = "\n".join(lines[2:]).strip() if len(lines) > 2 else ""

    # Cria no GitHub
    number = create_issue(repo, issue["name"], body)
    issue["id"] = number

    # Move para coluna correta no board
    col_name = config["boards"][board_id]["columns"][issue["column"]].get("name", issue["column"])
    move_card(config, number, board_id, col_name)

    # Apaga arquivo original e recria com padrão
    if filepath.exists():
        filepath.unlink()

    slug = _slugify(issue["name"])
    base = f"{number}-{slug}"
    col_path = BOARDS_DIR / board_id / issue["column"]
    col_path.mkdir(parents=True, exist_ok=True)

    new_path = col_path / f"{base}.md"
    new_history = col_path / f"{base}-history.md"
    new_write = col_path / f"{base}-write.md"

    new_path.write_text(f"# {issue['name']}\n\n{body}\n")
    new_history.write_text("")
    new_write.write_text("")

    # Limpa history/write antigos se existirem
    for key in ("history_path", "write_path"):
        old = Path(issue[key])
        if old.exists() and old != new_history and old != new_write:
            old.unlink()

    issue["path"] = str(new_path)
    issue["history_path"] = str(new_history)
    issue["write_path"] = str(new_write)
    issue["l-time"] = str(new_path.stat().st_mtime)
    issue["b-time"] = _now_iso()
    issue["status"] = "ok"


def _action_l_del(issue: dict, config: dict, board_id: str) -> None:
    """Fecha issue no GitHub e remove do board."""
    from src.github import close_issue

    repo = config["repo"]
    if issue["id"]:
        close_issue(repo, issue["id"])

    # Remove arquivos locais se ainda existirem
    for key in ("path", "history_path", "write_path"):
        p = Path(issue[key])
        if p.exists():
            p.unlink()


def _action_l_mv(issue: dict, config: dict, board_id: str) -> None:
    """Move card no board, checa write, cria history/write no novo local."""
    from src.github import move_card, post_comment

    repo = config["repo"]
    col_name = config["boards"][board_id]["columns"][issue["column"]].get("name", issue["column"])

    # Move no GitHub
    if issue["id"]:
        move_card(config, issue["id"], board_id, col_name)

    # Checa write - se tem conteúdo, posta como comentário
    write_path = Path(issue["write_path"])
    if write_path.exists():
        content = write_path.read_text().strip()
        if content and issue["id"]:
            post_comment(repo, issue["id"], content)
        write_path.write_text("")
    else:
        write_path.parent.mkdir(parents=True, exist_ok=True)
        write_path.write_text("")

    # Garante history no novo local
    history_path = Path(issue["history_path"])
    if not history_path.exists():
        history, _ = _build_history(repo, issue["id"]) if issue["id"] else ("", "")
        history_path.write_text(history)

    issue["column"] = _col_from_path(Path(issue["path"]))
    issue["status"] = "ok"


def _action_l_sync(issue: dict, repo: str) -> None:
    """Atualiza body no GitHub se principal mudou, posta write como comentário."""
    from src.github import update_issue_body, post_comment

    filepath = Path(issue["path"])
    write_path = Path(issue["write_path"])

    # Atualiza body se o arquivo principal mudou
    if filepath.exists() and issue["id"]:
        lines = filepath.read_text().splitlines()
        body = "\n".join(lines[2:]).strip() if len(lines) > 2 else ""
        update_issue_body(repo, issue["id"], body)

    # Se write tem conteúdo, posta como comentário e limpa
    if write_path.exists():
        content = write_path.read_text().strip()
        if content and issue["id"]:
            post_comment(repo, issue["id"], content)
            write_path.write_text("")

    issue["b-time"] = _now_iso()
    issue["status"] = "ok"
