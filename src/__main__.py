from src.config import load as load_config
from src.orchestrator import run_loop

VERSION = "0.1.0"

if __name__ == "__main__":
    config = load_config()
    run_loop(config)
