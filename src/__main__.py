import time

from src.config import load_config
from src.sync import sync
from src.issues import sync_issues
from src.github import RateLimitError, GitHubError


def main():
    config = load_config("pipe.yml")
    sync(config)

    sleeptime = config["pipe"].get("agent", {}).get("sleeptime", 5)
    print(f"Loop principal iniciado (intervalo: {sleeptime}s)")
    while True:
        try:
            sync_issues(config)
        except RateLimitError:
            print("  ⚠ Rate limit — aguardando próximo ciclo.")
        except GitHubError as e:
            print(f"  ⚠ Erro GitHub: {e}")
        except Exception as e:
            print(f"  ✖ Erro inesperado: {e}")
        time.sleep(sleeptime)


if __name__ == "__main__":
    main()
