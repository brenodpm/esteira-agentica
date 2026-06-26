"""Config core - carrega e valida pipe.yml."""

from pathlib import Path
import os
import yaml

PIPE_FILE = Path("pipe.yml")
SSH_KEY_ENV = "PIPE_SSH_KEY_FILE"


class ConfigError(Exception):
    """Erro de configuração do pipe.yml."""
    pass


def _require(data: dict, key: str, context: str):
    if key not in data:
        raise ConfigError(f"{context}: campo '{key}' é obrigatório")
    return data[key]


def _validate_env():
    key_path = os.environ.get(SSH_KEY_ENV, "").strip()
    if not key_path:
        raise ConfigError(
            f"Variável de ambiente '{SSH_KEY_ENV}' não definida ou vazia. "
            f"Defina com: export {SSH_KEY_ENV}=~/.ssh/id_ed25519"
        )
    if not Path(key_path).expanduser().exists():
        raise ConfigError(f"Arquivo SSH não encontrado: {key_path}")


def _validate_git(git: dict):
    _require(git, "repo", "git")
    _require(git, "flow", "git")
    
    flow = git["flow"]
    _require(flow, "base", "git.flow")
    
    for flow_id, flow_cfg in flow.items():
        if flow_id == "base":
            continue
        if "name" not in flow_cfg and "prefix" not in flow_cfg:
            raise ConfigError(f"git.flow.{flow_id}: requer 'name' ou 'prefix'")


def _validate_agents(agents: dict):
    for platform_id, platform in agents.items():
        for agent_id, agent_cfg in platform.items():
            _require(agent_cfg, "name", f"agents.{platform_id}.{agent_id}")


def _validate_boards(boards: dict):
    _require(boards, "platform", "boards")
    for board_id, board in boards.items():
        if board_id == "platform":
            continue
        _require(board, "name", f"boards.{board_id}")
        columns = _require(board, "columns", f"boards.{board_id}")
        
        for col_id, col in columns.items():
            _require(col, "name", f"boards.{board_id}.columns.{col_id}")


def _validate_log(log_cfg: dict):
    ttl = log_cfg.get("ttl")
    if ttl is not None and (not isinstance(ttl, int) or ttl < 1):
        raise ConfigError("log.ttl: deve ser inteiro >= 1")


def check_config() -> dict:
    """Valida e retorna configuração do pipe.yml."""
    _validate_env()
    
    if not PIPE_FILE.exists():
        raise ConfigError(f"Arquivo {PIPE_FILE} não encontrado")
    
    with open(PIPE_FILE, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    if not config:
        raise ConfigError("pipe.yml está vazio")
    
    if "log" in config:
        _validate_log(config["log"])
    
    git = _require(config, "git", "pipe.yml")
    _validate_git(git)
    
    agents = _require(config, "agents", "pipe.yml")
    _validate_agents(agents)
    
    boards = _require(config, "boards", "pipe.yml")
    _validate_boards(boards)
    
    return config
