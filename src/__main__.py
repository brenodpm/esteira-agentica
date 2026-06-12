import time

from src.config import load_config
from src.log import log, cleanup_logs
from src.sync import sync
from src.issues import sync_issues
from src.pick_task import pick_task, TODO_ADVANCE
from src.agent import run_agent
from src.github import RateLimitError, GitHubError


def main():
    config = load_config("pipe.yml")
    cleanup_logs(config.get("ttl-log", 10))
    sync(config)

    sleeptime = config["pipe"].get("agent", {}).get("sleeptime", 5)
    log.info("Loop iniciado")
    while True:
        try:
            sync_issues(config)
            task = pick_task(config)
            if task == TODO_ADVANCE:
                log.info("Auto-advance realizado — aguardando sync propagar")
            elif task:
                log.info("Tarefa selecionada: #%s [%s] %s (board: %s, col: %s)",
                            task["id"], task.get("created_at", "?"), task["name"],
                            task["board_id"], task["column"])
                run_agent(config, task)
            else:
                log.info("Nenhuma tarefa elegível")
                log.info("intervalo: %ds", sleeptime)
                time.sleep(sleeptime)
        except RateLimitError:
            log.warning("Rate limit — aguardando próximo ciclo")
        except GitHubError as e:
            log.error("Erro GitHub: %s", e)
        except Exception as e:
            log.error("Erro inesperado: %s", e, exc_info=True)


if __name__ == "__main__":
    main()
