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


def create_branch(config: dict, branch_type_or_title: str, name: str | None = None,
                  flow_key: str | None = None) -> str:
    """Cria branch.

    Modo novo (runner): create_branch(config, title, flow_key="feature")
      → usa config.git.flow[flow_key] para prefixo e base

    Modo legado (testes): create_branch(config, branch_type, name)
      → usa config.gitflow.prefixes
    """
    if name is not None:
        # Modo legado: branch_type + name
        gitflow = config.get("gitflow", {})
        prefixes = gitflow.get("prefixes", {})
        prefix = prefixes.get(branch_type_or_title, f"{branch_type_or_title}/")
        branch = f"{prefix}{name}"
        base = gitflow.get("branch_base", "main")
    else:
        # Modo novo: title + flow_key
        fk = flow_key or "feature"
        flow_cfg = config.get("git", {}).get("flow", {}).get(fk, {})
        prefix = flow_cfg.get("prefix", fk).rstrip("/") + "/"
        base_default = config.get("git", {}).get("flow", {}).get("base", "main")
        base = flow_cfg.get("create") or base_default
        branch = f"{prefix}{_slugify(branch_type_or_title)}"

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
