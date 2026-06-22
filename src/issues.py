"""Sincronização de issues entre GitHub Projects e disco local."""

import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from src.github import (
    fetch_issue_comments, fetch_updated_issues,
    fetch_board_items_graphql, resolve_project_metadata,
    create_issue, move_card, close_issue, update_issue_body,
    post_comment, get_issue_node_id, add_issue_to_project,
    GitHubError, RateLimitError, _gh,
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


LOGS_DIR = Path("logs")


def _append_write_to_log(issue_id: int, content: str) -> None:
    """Append conteúdo do write ao log mais recente da issue."""
    issue_log_dir = LOGS_DIR / str(issue_id)
    if not issue_log_dir.exists():
        return
    logs = sorted(issue_log_dir.glob("*.log"))
    if not logs:
        return
    with logs[-1].open("a", encoding="utf-8") as f:
        f.write(f"\n═══ WRITE ═══\n{content}\n")


def _col_name_to_id(config: dict, board_id: str) -> dict[str, str]:
    return {
        col.get("name", col_id): col_id
        for col_id, col in config["boards"][board_id]["columns"].items()
    }


def _col_id_to_name(config: dict, board_id: str) -> dict[str, str]:
    return {
        col_id: col.get("name", col_id)
        for col_id, col in config["boards"][board_id]["columns"].items()
    }


def _col_from_path(path: Path) -> str:
    """Extrai col_id do path: .pipe/boards/<board>/<col>/file.md"""
    return path.parent.name


def _build_history(repo: str, issue_number: int) -> tuple[str, str]:
    try:
        data = fetch_issue_comments(repo, issue_number)
    except RateLimitError:
        raise
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


def _scan_local_files(board_id: str) -> dict[int, Path]:
    """Retorna {issue_id: path} de todos os arquivos slug no board.
    
    Arquivos com prefixo numérico usam o número como ID.
    Arquivos sem prefixo numérico recebem ID negativo (temporário, para l-new).
    """
    board_path = BOARDS_DIR / board_id
    result = {}
    if not board_path.exists():
        return result
    next_temp_id = -1
    for col_dir in board_path.iterdir():
        if not col_dir.is_dir():
            continue
        for f in col_dir.iterdir():
            if f.is_file() and not f.name.endswith(("-history.md", "-write.md")) and f.suffix == ".md":
                match = re.match(r"^(\d+)-", f.name)
                if match:
                    result[int(match.group(1))] = f
                else:
                    result[next_temp_id] = f
                    next_temp_id -= 1
    return result


# ══════════════════════════════════════════════════════════════════════════════
# ETAPA 1: Local → Snapshot (detecção de mudanças locais)
# ══════════════════════════════════════════════════════════════════════════════


def _etapa1_local_para_snapshot(snapshot: dict, config: dict) -> None:
    """Vasculha diretórios e atualiza status no snapshot."""
    for board_id in config["boards"]:
        issues = snapshot.setdefault("issues", {}).setdefault(board_id, [])
        local_files = _scan_local_files(board_id)
        snapshot_ids = {i["id"] for i in issues}

        # Para cada issue existente no snapshot
        for issue in issues:
            if issue["status"] in ("b-new", "l-new", "b-del"):
                continue

            number = issue["id"]
            local_path = local_files.get(number)

            # Existe no snapshot mas não local → l-del
            if not local_path and not Path(issue["path"]).exists():
                if issue["status"] == "ok":
                    issue["status"] = "l-del"
                    log.debug("[%s] #%s detectado l-del (arquivo removido)", board_id, number)
                continue

            if not local_path:
                continue

            current_col = _col_from_path(local_path)

            # Coluna diferente → l-sync + atualizar paths
            if current_col != issue["column"]:
                log.debug("[%s] #%s detectado l-sync (movido %s → %s)", board_id, number, issue["column"], current_col)
                _handle_move(issue, local_path)
                continue

            # Mtime mais novo → l-sync
            file_mtime = str(local_path.stat().st_mtime)
            write_path = Path(issue["write_path"])
            write_mtime = str(write_path.stat().st_mtime) if write_path.exists() else "0"
            latest_mtime = max(file_mtime, write_mtime)

            if issue["l-time"] and latest_mtime > issue["l-time"]:
                issue["l-time"] = latest_mtime
                issue["status"] = "l-sync"
                log.debug("[%s] #%s detectado l-sync (arquivo modificado)", board_id, number)

        # Arquivos locais sem entrada no snapshot → l-new
        snapshot_paths = {i["path"] for i in issues}
        for file_id, file_path in local_files.items():
            if file_id in snapshot_ids:
                continue
            if str(file_path) in snapshot_paths:
                continue
            col_id = _col_from_path(file_path)
            slug = file_path.stem
            first_line = ""
            try:
                first_line = file_path.read_text().splitlines()[0].lstrip("# ").strip()
            except (IndexError, OSError):
                first_line = slug.split("-", 1)[1] if "-" in slug else slug
            issues.append({
                "id": file_id,
                "name": _sanitize_name(first_line),
                "column": col_id,
                "path": str(file_path),
                "history_path": str(file_path.parent / f"{slug}-history.md"),
                "write_path": str(file_path.parent / f"{slug}-write.md"),
                "l-time": str(file_path.stat().st_mtime),
                "b-time": None,
                "created_at": _now_iso(),
                "status": "l-new",
            })
            log.debug("[%s] #%s detectado l-new (%s)", board_id, file_id, file_path.name)
            snapshot_ids.add(file_id)


def _handle_move(issue: dict, local_path: Path) -> None:
    """Trata movimentação local: atualiza paths, cuida de órfãos."""
    new_col_path = local_path.parent
    slug = local_path.stem

    # Tratar órfãos
    old_history = Path(issue["history_path"])
    old_write = Path(issue["write_path"])

    if old_history.exists() and old_history.parent != new_col_path:
        old_history.unlink()

    if old_write.exists() and old_write.parent != new_col_path:
        new_write = new_col_path / f"{slug}-write.md"
        old_content = old_write.read_text().strip()
        if new_write.exists() and old_content:
            # Mesclar
            existing = new_write.read_text().strip()
            merged = f"{existing}\n\n{old_content}" if existing else old_content
            new_write.write_text(merged)
        elif old_content:
            new_write.write_text(old_content)
        old_write.unlink()

    issue["column"] = _col_from_path(local_path)
    issue["path"] = str(local_path)
    issue["history_path"] = str(new_col_path / f"{slug}-history.md")
    issue["write_path"] = str(new_col_path / f"{slug}-write.md")
    issue["l-time"] = str(local_path.stat().st_mtime)
    issue["status"] = "l-sync"


# ══════════════════════════════════════════════════════════════════════════════
# ETAPA 2: Snapshot → GitHub (propagar mudanças locais)
# ══════════════════════════════════════════════════════════════════════════════


def _etapa2_snapshot_para_github(snapshot: dict, config: dict) -> int:
    """Propaga mudanças locais para o GitHub. Retorna quantidade de ações."""
    repo = config["repo"]
    cache = snapshot.setdefault("cache", {})
    count = 0

    for board_id, issues in snapshot.get("issues", {}).items():
        to_remove = []
        col_id_to_name = _col_id_to_name(config, board_id)

        for i, issue in enumerate(issues):
            try:
                if issue["status"] == "l-sync":
                    _action_l_sync(issue, config, board_id, cache)
                    log.info("[%s] l-sync #%s → %s", board_id, issue["id"], issue["column"])
                    count += 1

                elif issue["status"] == "l-new":
                    if _action_l_new(issue, config, board_id, cache, issues):
                        to_remove.append(i)
                    else:
                        log.info("[%s] l-new #%s %s", board_id, issue["id"], issue["name"])
                    count += 1

                elif issue["status"] == "l-del":
                    allow_del = config["boards_meta"].get("allow-del-remote-issue", False)
                    _action_l_del(issue, config, board_id, allow_del)
                    log.info("[%s] l-del #%s", board_id, issue["id"])
                    to_remove.append(i)
                    count += 1

            except RateLimitError:
                log.info("[Sync Issues] Throttle na etapa 2 — salvando snapshot")
                for idx in reversed(to_remove):
                    issues.pop(idx)
                _save_snapshot(snapshot)
                raise
            except GitHubError as e:
                log.error("[%s] Erro GitHub issue #%s: %s", board_id, issue.get("id"), e)
                if "não encontrada no repo" in str(e):
                    for key in ("path", "history_path", "write_path"):
                        p = Path(issue.get(key, ""))
                        if p.exists():
                            p.unlink()
                    to_remove.append(i)

        for idx in reversed(to_remove):
            issues.pop(idx)

    return count


def _action_l_sync(issue: dict, config: dict, board_id: str, cache: dict) -> None:
    """l-sync: mover card se coluna mudou, atualizar body, postar write, reconstruir history."""
    repo = config["repo"]
    col_name = config["boards"][board_id]["columns"][issue["column"]].get("name", issue["column"])

    # Mover card
    if issue["id"]:
        move_card(config, issue["id"], board_id, col_name, cache)

    # Postar write como comentário ANTES de atualizar body (write modifica updatedAt)
    write_path = Path(issue["write_path"])
    wrote = False
    if write_path.exists():
        content = write_path.read_text().strip()
        if content and issue["id"]:
            _append_write_to_log(issue["id"], content)
            post_comment(repo, issue["id"], content)
            write_path.write_text("")
            wrote = True

    # Atualizar body apenas se arquivo local mudou
    filepath = Path(issue["path"])
    if filepath.exists() and issue["id"]:
        lines = filepath.read_text().splitlines()
        body = "\n".join(lines[2:]).strip() if len(lines) > 2 else ""
        update_issue_body(repo, issue["id"], body)

    # Reconstruir history apenas se houve write (novo comentário adicionado)
    if wrote and issue["id"]:
        history_path = Path(issue["history_path"])
        history, updated_at = _build_history(repo, issue["id"])
        history_path.parent.mkdir(parents=True, exist_ok=True)
        history_path.write_text(history)
        if updated_at:
            issue["b-time"] = updated_at

    issue["status"] = "ok"


def _action_l_new(issue: dict, config: dict, board_id: str, cache: dict, all_issues: list) -> bool:
    """l-new: criar issue no GitHub. Retorna True se duplicata (deve ser removida do snapshot)."""
    repo = config["repo"]
    filepath = Path(issue["path"])
    body = ""
    title = issue["name"]

    if filepath.exists():
        lines = filepath.read_text().splitlines()
        if lines and lines[0].startswith("# "):
            title = lines[0][2:].strip()
        body = "\n".join(lines[2:]).strip() if len(lines) > 2 else ""
    issue["name"] = title

    # Dedup: verificar se já existe issue com mesmo nome neste board
    for other in all_issues:
        if other is issue:
            continue
        if other["name"] == title and other["status"] != "l-new":
            log.info("[%s] dedup: '%s' já existe (#%s) — removendo local", board_id, title, other["id"])
            for key in ("path", "history_path", "write_path"):
                p = Path(issue.get(key, ""))
                if p.exists():
                    p.unlink()
            return True

    # Criar issue no GitHub
    number = create_issue(repo, title, body)
    issue["id"] = number

    # Renomear arquivo imediatamente para evitar re-detecção como l-new
    slug = _slugify(title)
    base = f"{number}-{slug}"
    col_path = BOARDS_DIR / board_id / issue["column"]
    col_path.mkdir(parents=True, exist_ok=True)

    new_path = col_path / f"{base}.md"
    new_history = col_path / f"{base}-history.md"
    new_write = col_path / f"{base}-write.md"

    if filepath.exists():
        filepath.unlink()
    new_path.write_text(f"# {title}\n\n{body}\n")
    new_history.write_text("")
    new_write.write_text("")

    # Limpar antigos
    for key in ("history_path", "write_path"):
        old = Path(issue[key])
        if old.exists() and old != new_history and old != new_write:
            old.unlink()

    issue["path"] = str(new_path)
    issue["history_path"] = str(new_history)
    issue["write_path"] = str(new_write)
    issue["l-time"] = str(new_path.stat().st_mtime)

    # Adicionar ao project e cachear item_id
    node_id = get_issue_node_id(repo, number)
    item_id = add_issue_to_project(config, board_id, node_id, cache)
    meta = cache.get(board_id, {})
    meta.setdefault("items", {})[str(number)] = item_id

    # Mover para coluna correta
    col_name = config["boards"][board_id]["columns"][issue["column"]].get("name", issue["column"])
    move_card(config, number, board_id, col_name, cache)

    issue["b-time"] = _now_iso()
    issue["status"] = "ok"
    return False


def _action_l_del(issue: dict, config: dict, board_id: str, allow_del: bool) -> None:
    """l-del: fechar issue no GitHub se permitido, ou só remover do snapshot."""
    repo = config["repo"]
    if allow_del and issue["id"] and issue["id"] > 0:
        post_comment(repo, issue["id"], "Issue removida via agent")
        close_issue(repo, issue["id"])
    # Remove arquivos locais restantes
    for key in ("path", "history_path", "write_path"):
        p = Path(issue.get(key, ""))
        if p and p.exists():
            p.unlink()


# ══════════════════════════════════════════════════════════════════════════════
# ETAPA 3: GitHub → Snapshot (buscar mudanças remotas)
# ══════════════════════════════════════════════════════════════════════════════


def _etapa3_github_para_snapshot(snapshot: dict, config: dict) -> int:
    """Busca issues modificadas no GitHub e aplica no snapshot/local. Retorna ações.

    Otimizado: 1 REST (updated issues) + GraphQL apenas para boards com updates.
    Usa body do board items em vez de chamada separada por issue.
    fetch_issue_comments apenas para issues realmente modificadas (history).
    """
    repo = config["repo"]
    last_sync = snapshot.get("last_sync")
    cache = snapshot.setdefault("cache", {})
    count = 0

    if not last_sync:
        return count

    try:
        updated_numbers = set(fetch_updated_issues(repo, last_sync))
    except (RateLimitError, GitHubError) as e:
        log.warning("Etapa 3: falha ao buscar issues modificadas: %s", e)
        return count

    if not updated_numbers:
        return count

    for board_id, issues in snapshot.get("issues", {}).items():
        # Skip board se nenhuma issue dele foi atualizada
        board_numbers = {i["id"] for i in issues if i["status"] == "ok"}
        if not (board_numbers & updated_numbers):
            continue

        name_to_id = _col_name_to_id(config, board_id)

        try:
            meta = resolve_project_metadata(config, board_id, cache)
            remote_items = fetch_board_items_graphql(meta["project_id"])
        except RateLimitError:
            raise
        except GitHubError as e:
            log.warning("Etapa 3: falha ao buscar items do board '%s': %s", board_id, e)
            continue

        # Indexar items remotos por number para acesso O(1)
        remote_by_number = {}
        items_cache = meta.setdefault("items", {})
        for item in remote_items:
            remote_by_number[item["number"]] = item
            items_cache[str(item["number"])] = item["item_id"]

        # Processar issues atualizadas
        for issue in issues:
            if issue["status"] != "ok":
                continue
            if issue["id"] not in updated_numbers:
                continue

            remote_item = remote_by_number.get(issue["id"])
            if not remote_item:
                continue

            remote_updated = remote_item["updated_at"]
            if not remote_updated or remote_updated <= (issue.get("b-time") or ""):
                continue

            # Body vem do GraphQL — sem chamada extra
            remote_body = remote_item.get("body", "")
            filepath = Path(issue["path"])
            if filepath.exists():
                local_content = filepath.read_text()
                new_content = f"# {issue['name']}\n\n{remote_body}\n"
                if local_content != new_content:
                    filepath.write_text(new_content)
                    issue["l-time"] = str(filepath.stat().st_mtime)
                    log.debug("[%s] #%s b-sync body atualizado localmente", board_id, issue["id"])

            # History — UMA chamada REST por issue que realmente mudou
            try:
                data = fetch_issue_comments(repo, issue["id"])
                comments = data.get("comments", [])
                if comments:
                    history_path = Path(issue["history_path"])
                    lines = []
                    for c in comments:
                        lines.append(f"{c['author']['login']} - {c['createdAt']}")
                        lines.append(c["body"])
                        lines.append("--------")
                        lines.append("")
                    history_path.write_text("\n".join(lines))
            except RateLimitError:
                raise
            except GitHubError:
                pass

            # Write em branco se não existe
            write_path = Path(issue["write_path"])
            write_path.parent.mkdir(parents=True, exist_ok=True)
            if not write_path.exists():
                write_path.write_text("")

            # Coluna — já temos do remote_item (sem chamada extra)
            remote_col_name = remote_item["status"]
            remote_col_id = name_to_id.get(remote_col_name)
            if remote_col_id and remote_col_id != issue["column"]:
                log.debug("[%s] #%s b-sync coluna remota mudou (%s → %s)", board_id, issue["id"], issue["column"], remote_col_id)
                _move_local_files(issue, board_id, remote_col_id)

            issue["b-time"] = remote_updated
            log.debug("[%s] #%s b-sync aplicado (b-time=%s)", board_id, issue["id"], remote_updated)
            count += 1

    return count


def _move_local_files(issue: dict, board_id: str, new_col_id: str) -> None:
    """Move os 3 arquivos locais para a nova coluna."""
    new_col_path = BOARDS_DIR / board_id / new_col_id
    new_col_path.mkdir(parents=True, exist_ok=True)

    for key in ("path", "history_path", "write_path"):
        old = Path(issue[key]) if issue.get(key) else None
        if old and old.exists():
            new = new_col_path / old.name
            old.rename(new)
            issue[key] = str(new)
        elif old:
            issue[key] = str(new_col_path / old.name)

    issue["column"] = new_col_id


# ══════════════════════════════════════════════════════════════════════════════
# ETAPA 4: Remoção de resíduos (b-del e b-new)
# ══════════════════════════════════════════════════════════════════════════════


def _etapa4_residuos(snapshot: dict, config: dict) -> int:
    """Remove b-del e cria localmente b-new. Retorna ações."""
    repo = config["repo"]
    count = 0

    for board_id, issues in list(snapshot.get("issues", {}).items()):
        to_remove = []

        for i, issue in enumerate(issues):
            if issue["status"] == "b-del":
                # Remover arquivos locais
                for key in ("path", "history_path", "write_path"):
                    p = Path(issue[key]) if issue.get(key) else None
                    if p and p.exists():
                        p.unlink()
                to_remove.append(i)
                log.info("[%s] b-del #%s removido localmente", board_id, issue["id"])
                count += 1

            elif issue["status"] == "b-new":
                try:
                    _action_b_new(issue, config, board_id, repo)
                except (RateLimitError, GitHubError) as e:
                    log.warning("[%s] b-new #%s falhou (%s) — será retentado", board_id, issue["id"], e)
                    # Salvar snapshot parcial para não perder progresso das anteriores
                    for idx in reversed(to_remove):
                        issues.pop(idx)
                    _save_snapshot(snapshot)
                    return count
                log.info("[%s] b-new #%s %s criado localmente", board_id, issue["id"], issue["name"])
                count += 1

        for idx in reversed(to_remove):
            issues.pop(idx)

    return count


def _action_b_new(issue: dict, config: dict, board_id: str, repo: str) -> None:
    """Cria os 3 arquivos locais para issue vinda do board."""
    slug = _slugify(issue["name"])
    base = f"{issue['id']}-{slug}"

    # Resolver col_id (pode ser nome da coluna se veio do remote)
    col_id = issue["column"]
    name_to_id = _col_name_to_id(config, board_id)
    if col_id in name_to_id:
        col_id = name_to_id[col_id]
        issue["column"] = col_id

    col_path = BOARDS_DIR / board_id / col_id
    col_path.mkdir(parents=True, exist_ok=True)

    filepath = col_path / f"{base}.md"
    history_path = col_path / f"{base}-history.md"
    write_path = col_path / f"{base}-write.md"

    # Body: usar do cache (_body) se disponível, senão buscar (offline-safe)
    body = issue.pop("_body", None)
    if body is None:
        if filepath.exists():
            # Arquivo já existe no disco (retry após falha anterior) — usar conteúdo local
            lines = filepath.read_text().splitlines()
            body = "\n".join(lines[2:]).strip() if len(lines) > 2 else ""
        else:
            try:
                out = _gh("issue", "view", str(issue["id"]), "--repo", repo, "--json", "body")
                body = json.loads(out).get("body", "")
            except (RateLimitError, GitHubError):
                body = ""

    filepath.write_text(f"# {issue['name']}\n\n{body}\n")

    # History: fallback offline se API indisponível
    try:
        history, updated_at = _build_history(repo, issue["id"])
    except RateLimitError:
        history, updated_at = "", ""
    history_path.write_text(history)

    # Write (vazio)
    if not write_path.exists():
        write_path.write_text("")

    issue["path"] = str(filepath)
    issue["history_path"] = str(history_path)
    issue["write_path"] = str(write_path)
    issue["l-time"] = str(filepath.stat().st_mtime)
    issue["b-time"] = updated_at or issue.get("b-time") or _now_iso()
    issue["status"] = "ok"


# ══════════════════════════════════════════════════════════════════════════════
# ENTRADA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════


def _validate_directories(config: dict) -> None:
    """Valida diretórios em .pipe/boards/ — cria faltantes, move extras para 'todo'."""
    if not BOARDS_DIR.exists():
        return

    expected_boards = set(config["boards"].keys())
    existing_boards = {d.name for d in BOARDS_DIR.iterdir() if d.is_dir()}

    for missing in expected_boards - existing_boards:
        (BOARDS_DIR / missing).mkdir()
        log.info("[validate] criado diretório board: %s", missing)
    for extra in existing_boards - expected_boards:
        extra_path = BOARDS_DIR / extra
        if not any(extra_path.rglob("*.md")):
            extra_path.rmdir()
            log.info("[validate] removido diretório board vazio: %s", extra)

    for board_id, board in config["boards"].items():
        board_path = BOARDS_DIR / board_id
        if not board_path.exists():
            continue
        expected_cols = set(board.get("columns", {}).keys())
        todo_col = board.get("todo")
        if not todo_col:
            continue
        todo_path = board_path / todo_col
        todo_path.mkdir(exist_ok=True)

        # Arquivos soltos no nível do board → mover para todo
        for f in board_path.iterdir():
            if f.is_file():
                f.rename(todo_path / f.name)
                log.info("[validate] movido %s → %s/%s (solto no board)", f.name, board_id, todo_col)

        existing_cols = {d.name for d in board_path.iterdir() if d.is_dir()}

        for missing in expected_cols - existing_cols:
            (board_path / missing).mkdir()
            log.info("[validate] criado diretório coluna: %s/%s", board_id, missing)

        for extra in existing_cols - expected_cols:
            extra_path = board_path / extra
            for f in extra_path.iterdir():
                if f.is_file():
                    f.rename(todo_path / f.name)
                    log.info("[validate] movido %s → %s/%s (coluna extra)", f.name, board_id, todo_col)
            extra_path.rmdir()
            log.info("[validate] removido diretório extra: %s/%s", board_id, extra)


def sync_issues(config: dict) -> bool:
    """Sincronização de issues nas 4 etapas. Retorna True se houve ações."""
    log.info("[Sync Issues] Sincronização de issues...")
    _validate_directories(config)
    snapshot = _load_snapshot()
    if "issues" not in snapshot:
        snapshot["issues"] = {}

    count = 0

    # Etapa 1: Local → Snapshot
    _etapa1_local_para_snapshot(snapshot, config)

    # Etapa 2: Snapshot → GitHub
    count += _etapa2_snapshot_para_github(snapshot, config)

    # Etapa 3: GitHub → Snapshot
    try:
        count += _etapa3_github_para_snapshot(snapshot, config)
    except RateLimitError:
        log.info("[Sync Issues] Throttle na etapa 3 — salvando snapshot")
        _save_snapshot(snapshot)
        raise

    # Etapa 4: Remoção de resíduos
    count += _etapa4_residuos(snapshot, config)

    # Atualizar last_sync
    snapshot["last_sync"] = _now_iso()
    _save_snapshot(snapshot)

    return count > 0


def sync_issues_local(config: dict) -> bool:
    """Sincronização local apenas (etapas 1 e 4). Usado durante penalty box."""
    log.info("[Sync Issues] Sincronização local (penalty ativo)...")
    _validate_directories(config)
    snapshot = _load_snapshot()
    if "issues" not in snapshot:
        snapshot["issues"] = {}

    # Etapa 1: Local → Snapshot
    _etapa1_local_para_snapshot(snapshot, config)

    # Etapa 4: Remoção de resíduos locais (b-new cria arquivos, b-del remove)
    count = _etapa4_residuos(snapshot, config)

    _save_snapshot(snapshot)
    return count > 0
