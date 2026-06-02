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


def create_branch(config: dict, branch_type_or_title: str, name: str | None = None) -> str:
    """Cria branch a partir do título da issue ou do tipo+nome explícito.

    Assinatura nova: create_branch(config, feature_title)
    Assinatura legada: create_branch(config, branch_type, name)
    """
    gitflow = config.get("gitflow", {})

    if name is None:
        # Nova assinatura: branch_type_or_title é o título da issue
        flow = gitflow.get("flow", {})
        prefix = "feature/"
        for cfg in flow.values():
            if isinstance(cfg, dict) and cfg.get("prefix"):
                prefix = cfg["prefix"].rstrip("/") + "/"
                break
        # Fallback para prefixes legado
        if prefix == "feature/" and "prefixes" in gitflow:
            prefix = gitflow["prefixes"].get("feature", "feature/")
        slug = _slugify(branch_type_or_title)
        branch = f"{prefix}{slug}"
    else:
        # Assinatura legada: branch_type + name
        prefixes = gitflow.get("prefixes", {})
        prefix = prefixes.get(branch_type_or_title, f"{branch_type_or_title}/")
        branch = f"{prefix}{name}"

    base = gitflow.get("branch_base", "main")
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
