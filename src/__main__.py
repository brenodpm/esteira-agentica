from src.core.log import log
from src.core.config import check_config as validate_config, ConfigError, SSH_KEY_ENV
from src.core.board import Board, PenaltyException
from src.core.snapshot import Snapshot
from src.core.change_queue import ChangeQueue, QUEUE_FILE
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
        log.configure(config)
        log.cleanup()
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

    # Limpa a fila de mudanças de execuções anteriores
    if QUEUE_FILE.exists():
        log.info("Startup", "Removendo fila de mudanças anterior")
        QUEUE_FILE.unlink()

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
    log.info("Board", "Sincronizando estrutura local")

    # Criar diretórios e sincronizar snapshot local por board
    for board_id in board.board_ids(config):
        board_cfg = config["boards"][board_id]
        columns = board_cfg.get("columns", {})

        # Criar diretórios .pipe/boards/<board_id>/<col_id>
        board_dir = Path(".pipe/boards") / board_id
        board_dir.mkdir(parents=True, exist_ok=True)
        for col_id in columns:
            (board_dir / col_id).mkdir(exist_ok=True)

        # Sincronizar snapshot local (estrutura de colunas)
        snap = Snapshot(board_id).load()
        snap.board = {col_id: col["name"] for col_id, col in columns.items()}
        snap.save()

    # Sync online
    log.info("Board", "Sincronizando boards remotos")
    attempt = 0
    while True:
        try:
            attempt += 1
            if attempt > 1:
                log.info("Board", f"Sincronizando boards remotos - tentativa {attempt}")
            board.sync_boards(config)
            break
        except PenaltyException as e:
            back_at = (datetime.now() + timedelta(seconds=e.wait_seconds)).strftime('%H:%M:%S')
            log.warning("Board", f"Rate limit - retorna às {back_at}")
            time.sleep(e.wait_seconds)

    # Detectar mudanças remotas
    log.info("Board", "Detectando mudanças remotas")
    queue = ChangeQueue()
    total = 0
    for board_id in board.board_ids(config):
        snap = Snapshot(board_id).load()
        attempt = 0
        while True:
            try:
                attempt += 1
                log.info("Board", f"Analisando board '{board_id}'"
                         + (f" - tentativa {attempt}" if attempt > 1 else ""))
                total += board.detect_board_changes(board_id, snap, queue)
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


_BANNER = r"""
 _____ ____ _____ _____ ___ ____      _
| ____/ ___|_   _| ____|_ _|  _ \   / \
|  _| \___ \ | | |  _|  | || |_) | / _ \
| |___ ___) || | | |___ | ||  _ < / ___ \
|_____|____/ |_| |_____|___|_| \_/_/   \_\
"""


def main():
    global board
    print(_BANNER)
    log.separator()
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
