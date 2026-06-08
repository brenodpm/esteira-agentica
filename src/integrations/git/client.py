import re
import subprocess


def _git(*args) -> str:
    try:
        result = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.stderr) from e


def _slugify(text: str) -> str:
    import unicodedata
    slug = unicodedata.normalize("NFKD", text.lower().strip())
    slug = slug.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug[:60]


def _base_branch(config: dict) -> str:
    return config.get("git", {}).get("flow", {}).get("base", "main")


def _is_prefix_ref(config: dict, value: str) -> bool:
    """Verifica se value é um prefixo de outro flow (branch dinâmica)."""
    flows = config.get("git", {}).get("flow", {})
    for key, flow in flows.items():
        if isinstance(flow, dict) and flow.get("prefix") == value:
            return True
    return False


def resolve_branch(config: dict, ref: str, issue: dict | None = None) -> str:
    """Resolve o nome real da branch a partir de ref.

    Se ref é branch fixa (não é prefixo de nenhum flow) → retorna ref.
    Se ref é prefixo → busca na issue via label 'branch:<nome>' ou body '<!-- branch: <nome> -->'.
    """
    if not _is_prefix_ref(config, ref):
        return ref

    if issue:
        # 1. Busca label 'branch:<nome>'
        labels = [l["name"] if isinstance(l, dict) else l for l in issue.get("labels", [])]
        for label in labels:
            if label.startswith("branch:"):
                return label[len("branch:"):]

        # 2. Busca no body '<!-- branch: <nome> -->'
        body = issue.get("body") or ""
        match = re.search(r"<!--\s*branch:\s*(.+?)\s*-->", body)
        if match:
            return match.group(1)

    raise RuntimeError(
        f"Branch dinâmica não resolvida: '{ref}' é prefixo de flow mas a issue "
        f"não possui label 'branch:<nome>' nem marcador '<!-- branch: <nome> -->' no body."
    )


def fetch_and_checkout(branch: str) -> None:
    """Faz fetch e checkout da branch, atualizando com a última versão do servidor."""
    _git("fetch", "origin", branch)
    _git("checkout", branch)
    _git("pull", "origin", branch)


def create_branch(config: dict, branch_type_or_title: str, name: str | None = None,
                  flow_key: str | None = None, issue: dict | None = None) -> str:
    """Cria branch de trabalho.

    Modo novo (runner): create_branch(config, title, flow_key="feature", issue=issue)
      → resolve a branch base (fixa ou dinâmica via issue)
      → faz fetch+pull da base
      → cria branch de trabalho com o prefixo do flow

    Modo legado (testes): create_branch(config, branch_type, name)
      → usa config.gitflow.prefixes
    """
    if name is not None:
        # Modo legado
        gitflow = config.get("gitflow", {})
        prefixes = gitflow.get("prefixes", {})
        prefix = prefixes.get(branch_type_or_title, f"{branch_type_or_title}/")
        branch = f"{prefix}{name}"
        base = gitflow.get("branch_base", "main")
        _git("checkout", "-b", branch, base)
        return branch

    # Modo novo
    fk = flow_key or "feature"
    flow_cfg = config.get("git", {}).get("flow", {}).get(fk, {})
    prefix = flow_cfg.get("prefix", fk).rstrip("/") + "/"
    create_ref = flow_cfg.get("create") or _base_branch(config)

    # Resolve branch base (fixa ou dinâmica)
    base = resolve_branch(config, create_ref, issue)

    # Fetch + pull da base antes de criar
    fetch_and_checkout(base)

    branch = f"{prefix}{_slugify(branch_type_or_title)}"
    _git("checkout", "-b", branch)
    return branch


def resolve_merge_target(config: dict, flow_key: str, issue: dict | None = None) -> str:
    """Resolve a branch alvo do PR a partir do flow.merge."""
    flow_cfg = config.get("git", {}).get("flow", {}).get(flow_key, {})
    merge_ref = flow_cfg.get("merge") or _base_branch(config)
    return resolve_branch(config, merge_ref, issue)


def commit(config: dict, message: str, files: list[str] | None = None) -> bool:
    """Commita mudanças. Retorna True se houve commit, False se não havia nada."""
    if files is None:
        _git("add", "-A")
    else:
        _git("add", *files)
    if not _git("status", "--porcelain").strip():
        return False
    _git("commit", "-m", message)
    return True


def push(branch: str) -> None:
    _git("push", "-u", "origin", branch)


def current_branch() -> str:
    return _git("rev-parse", "--abbrev-ref", "HEAD").strip()


def cleanup(config: dict) -> None:
    """Checkout para branch base e apaga todas as branches locais exceto a base."""
    base = _base_branch(config)
    _git("checkout", base)
    _git("pull", "origin", base)
    # Lista branches locais exceto a base
    output = _git("branch").strip()
    for line in output.splitlines():
        branch = line.strip().lstrip("* ").strip()
        if branch and branch != base:
            try:
                _git("branch", "-D", branch)
            except RuntimeError:
                pass


def delete_branch(branch: str, config: dict | None = None) -> None:
    """Deleta branch local e remota, voltando para a branch base."""
    base = _base_branch(config) if config else "main"
    _git("checkout", base)
    _git("branch", "-D", branch)
    try:
        _git("push", "origin", "--delete", branch)
    except RuntimeError:
        pass
