"""Log core - escreve em arquivo e terminal simultaneamente."""

import logging
import re
from datetime import date
from pathlib import Path

LOG_DIR = Path("logs")

_RESET = "\033[0m"
_BOLD = "\033[1m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_WHITE = "\033[37m"

# Cor dos colchetes por nível (conteúdo fora dos colchetes fica na cor padrão)
_LEVEL_COLOR = {
    logging.DEBUG: _WHITE,    # trace
    logging.INFO: _BOLD,
    logging.WARNING: _YELLOW,
    logging.ERROR: _RED,
}

_BRACKET = re.compile(r"\[([^\]]+)\]")


class _ColorFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        color = _LEVEL_COLOR.get(record.levelno, _BOLD)
        return _BRACKET.sub(f"{color}[\\1]{_RESET}", msg)


class Log:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self._logger = logging.getLogger("esteira")
        if self._logger.handlers:
            return

        self._logger.setLevel(logging.INFO)

        # Arquivo
        log_file = LOG_DIR / f"{date.today().strftime('%Y-%m-%d')}.log"
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"))
        self._logger.addHandler(fh)

        # Terminal
        ch = logging.StreamHandler()
        ch.setFormatter(_ColorFormatter("%(message)s"))
        self._logger.addHandler(ch)

    def set_level(self, level: str):
        self._logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    def info(self, module: str, msg: str, *args):
        self._logger.info(f"[{module}] {msg}", *args)

    def warning(self, module: str, msg: str, *args):
        self._logger.warning(f"[{module}] {msg}", *args)

    def error(self, module: str, msg: str, *args, **kwargs):
        self._logger.error(f"[{module}] {msg}", *args, **kwargs)

    def debug(self, module: str, msg: str, *args):
        self._logger.debug(f"[{module}] {msg}", *args)


log = Log()
