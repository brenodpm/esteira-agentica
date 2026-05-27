import subprocess


def _git(*args) -> str:
    try:
        result = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.stderr) from e


def create_branch(config: dict, branch_type: str, name: str) -> str:
    prefix = config["gitflow"]["prefixes"][branch_type]
    branch = f"{prefix}{name}"
    base = config["gitflow"]["branch_base"]
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
