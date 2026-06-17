"""Logging com arquivo diário em logs/yyyy-MM-dd.log."""

import logging
from datetime import date
from pathlib import Path

LOG_DIR = Path("logs")

_RED = "\033[31m"
_BLUE_BOLD = "\033[1;34m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


class _ColorFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        if record.levelno >= logging.WARNING:
            return f"{_RED}{msg}{_RESET}"
        if "['" in msg or "[Agent]" in msg:
            return f"{_BLUE_BOLD}{msg}{_RESET}"
        import re
        msg = re.sub(r"\[([^\]]+)\]", f"{_BOLD}[\\1]{_RESET}", msg)
        return msg


def setup() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("esteira")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)

    # Arquivo: logs/yyyy-MM-dd.log
    log_file = LOG_DIR / f"{date.today().strftime('%Y-%m-%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(file_handler)

    # Terminal (colorido)
    console = logging.StreamHandler()
    console.setFormatter(_ColorFormatter("%(message)s"))
    logger.addHandler(console)

    return logger


log = setup()


def cleanup_logs(ttl_days: int = 10):
    """Remove arquivos com mais de ttl_days e diretórios vazios em logs/."""
    if not LOG_DIR.exists():
        return
    now = date.today()
    for path in sorted(LOG_DIR.rglob("*")):
        if path.is_file():
            age = (now - date.fromtimestamp(path.stat().st_mtime)).days
            if age > ttl_days:
                path.unlink()
    # Remover diretórios vazios (bottom-up)
    for path in sorted(LOG_DIR.rglob("*"), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
