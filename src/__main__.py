from src.core.log import log
from src.core.config import check_config as validate_config, ConfigError, SSH_KEY_ENV
from src.core.board import Board, PenaltyException
from src.core.snapshot import Snapshot
from src.core.change_queue import ChangeQueue
from src.adapters.github_board import GitHubBoardAdapter
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import shutil
import os
import time

REPO_DIR = Path("repo")
SSH_DIR = Path.home() / ".ssh"

board: Board = None

ADAPTERS = {
    "github": GitHubBoardAdapter,
}


def check_config():
    log.info("Config", "Validando pipe.yml")
    try:
        config = validate_config()
        log.info("Config", "pipe.yml válido")
        return config
    except ConfigError as e:
        log.error("Config", str(e))
        raise SystemExit(1)


def _setup_ssh():
    SSH_DIR.mkdir(mode=0o700, exist_ok=True)
    key_file = SSH_DIR / "id_pipe"
    source_key = Path(os.environ[SSH_KEY_ENV]).expanduser()
    key_file.write_bytes(source_key.read_bytes())
    key_file.chmod(0o600)
    
    # Configura SSH para usar essa chave no github
    ssh_config = SSH_DIR / "config"
    config_block = "\nHost github.com\n  IdentityFile ~/.ssh/id_pipe\n  StrictHostKeyChecking no\n"
    if ssh_config.exists():
        content = ssh_config.read_text()
        if "id_pipe" not in content:
            ssh_config.write_text(content + config_block)
    else:
        ssh_config.write_text(config_block)


def startup(config: dict):
    log.info("Startup", "Verificando repositórios")
    _setup_ssh()
    REPO_DIR.mkdir(exist_ok=True)
    
    expected = set(config["git"]["repo"].keys())
    existing = {d.name for d in REPO_DIR.iterdir() if d.is_dir()}
    
    # Clonar faltantes
    for repo_id in expected - existing:
        url = config["git"]["repo"][repo_id]
        log.info("Startup", f"Clonando {repo_id}")
        subprocess.run(["git", "clone", url, repo_id], cwd=REPO_DIR, check=True)
    
    # Remover extras
    for repo_id in existing - expected:
        log.info("Startup", f"Removendo {repo_id}")
        shutil.rmtree(REPO_DIR / repo_id)


def first_board_sync(config: dict):
    global board
    log.info("Board", "Sincronizando estrutura de boards")
    while True:
        try:
            board.sync_boards(config)
            break
        except PenaltyException as e:
            log.warning("Board", f"Rate limit - retorna às {(datetime.now() + timedelta(seconds=e.wait_seconds)).strftime('%H:%M:%S')}")
            time.sleep(e.wait_seconds)

    log.info("Board", "Detectando mudanças remotas")
    snapshot = Snapshot().load()
    queue = ChangeQueue()
    total = 0
    for board_id in board.board_ids(config):
        while True:
            try:
                total += board.detect_board_changes(board_id, snapshot, queue)
                break
            except PenaltyException as e:
                back_at = (datetime.now() + timedelta(seconds=e.wait_seconds)).strftime('%H:%M:%S')
                log.warning("Board", f"Rate limit em '{board_id}' - retorna às {back_at}")
                time.sleep(e.wait_seconds)
    log.info("Board", f"{total} mudança(s) remota(s) adicionada(s) à fila")


def sync_board():
    pass


def keep_task():
    pass


def call_agent():
    pass


def sleep_time():
    pass


def main():
    global board
    log.info("Pipe", "Iniciando esteira agêntica")

    config = check_config()
    startup(config)
    
    platform = config["boards"]["platform"]
    if platform not in ADAPTERS:
        log.error("Config", f"Plataforma '{platform}' não suportada. Use: {list(ADAPTERS.keys())}")
        raise SystemExit(1)
    
    adapter = ADAPTERS[platform]()
    board = Board(adapter)
    board.connect(config)
    
    first_board_sync(config)

    running = True
    while running:
        sync_board()
        keep_task()
        call_agent()
        sleep_time()


if __name__ == "__main__":
    main()
