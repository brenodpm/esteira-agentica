"""Logging com rotação diária."""

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

LOG_DIR = Path(".pipe/logs")


def setup() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("esteira")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)

    # Arquivo: rotação diária, mantém 10 dias
    file_handler = TimedRotatingFileHandler(
        LOG_DIR / "esteira.log", when="midnight", backupCount=10, encoding="utf-8"
    )
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(file_handler)

    # Terminal: só etapa atual (nível INFO+)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console)

    return logger


log = setup()
