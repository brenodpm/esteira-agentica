import time

from src.config import load_config
from src.log import log
from src.sync import sync
from src.issues import sync_issues
from src.github import RateLimitError, GitHubError


def main():
    config = load_config("pipe.yml")
    sync(config)

    sleeptime = config["pipe"].get("agent", {}).get("sleeptime", 5)
    log.info("Loop iniciado (intervalo: %ds)", sleeptime)
    while True:
        try:
            sync_issues(config)
        except RateLimitError:
            log.warning("Rate limit — aguardando próximo ciclo")
        except GitHubError as e:
            log.error("Erro GitHub: %s", e)
        except Exception as e:
            log.error("Erro inesperado: %s", e, exc_info=True)
        time.sleep(sleeptime)


if __name__ == "__main__":
    main()
