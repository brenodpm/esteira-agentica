import re
import subprocess


def _git(*args) -> str:
    try:
        result = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.stderr) from e


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug[:60]


def create_branch(config: dict, title: str, flow_key: str = "feature",
                  base_override: str | None = None) -> str:
    """Cria branch para a issue usando o flow_key do board.

    Determina prefixo e base a partir de config.git.flow[flow_key].
    base_override substitui o 'create' do flow se fornecido.
    """
    flow_cfg = config.get("git", {}).get("flow", {}).get(flow_key, {})
    prefix = flow_cfg.get("prefix", flow_key).rstrip("/") + "/"
    base = base_override or flow_cfg.get("create") or config.get("git", {}).get("flow", {}).get("base", "main")

    branch = f"{prefix}{_slugify(title)}"
    _git("checkout", "-b", branch, base)
    return branch


def commit(config: dict, message: str, files: list[str] | None = None) -> None:
    if files is None:
        _git("add", "-A")
    else:
        _git("add", *files)
    _git("commit", "-m", message)


def push(branch: str) -> None:
    _git("push", "-u", "origin", branch)


def current_branch() -> str:
    return _git("rev-parse", "--abbrev-ref", "HEAD").strip()


def delete_branch(branch: str) -> None:
    _git("checkout", "main")
    _git("branch", "-D", branch)
    try:
        _git("push", "origin", "--delete", branch)
    except RuntimeError:
        pass  # branch remota pode já não existir
