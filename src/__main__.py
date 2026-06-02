import sys
from src.config import load as load_config
from src.orchestrator import run_loop
from src.integrations.github import sync_boards

VERSION = "0.1.0"


def main() -> None:
    args = sys.argv[1:]
    config = load_config("esteira.yml")

    if args and args[0] == "sync":
        print(f"Sincronizando boards com GitHub Projects V2...")
        sync_boards(config)
        print("Sincronização concluída.")
        return

    print(f"Esteira Agêntica v{VERSION} — repo: {config['repo']}")
    run_loop(config)


if __name__ == "__main__":
    sys.exit(main())
