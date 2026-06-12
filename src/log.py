"""Logging com arquivo diário em logs/yyyy-MM-dd.log."""

import logging
from datetime import date
from pathlib import Path

LOG_DIR = Path("logs")


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

    # Terminal
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(message)s"))
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
