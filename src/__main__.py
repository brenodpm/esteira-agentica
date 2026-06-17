import time
from datetime import datetime, timezone, timedelta

from src.config import load_config
from src.log import log, cleanup_logs
from src.sync import sync, should_full_sync, full_sync, _load_snapshot, _save_snapshot
from src.issues import sync_issues
from src.pick_task import pick_task, TODO_ADVANCE
from src.agent import run_agent
from src.github import RateLimitError, GitHubError

_tz = timezone(timedelta(hours=-3))


def _log_wake(sleeptime):
    wake = datetime.now(_tz) + timedelta(seconds=sleeptime)
    log.info("[Sleep Time] Retorno às %s", wake.strftime("%H:%M:%S"))


def main():
    config = load_config("pipe.yml")
    cleanup_logs(config.get("ttl-log", 10))

    # sync() roda apenas uma vez ao iniciar
    snapshot = sync(config)

    sleeptime = config["pipe"].get("agent", {}).get("sleeptime", 5)
    log.info("[Pipe] Loop iniciado")
    while True:
        try:
            # Verificar virada de dia a cada iteração
            snapshot = _load_snapshot()
            if should_full_sync(snapshot):
                log.info("[Pipe] Virada de dia detectada — full sync")
                full_sync(config, snapshot)

            synced = sync_issues(config)
            task = pick_task(config)
            if task == TODO_ADVANCE:
                log.info("[Pipe] Auto-advance realizado — aguardando sync propagar")
            elif task:
                log.info("[Pipe] Tarefa selecionada: #%s [%s] %s (board: %s, col: %s)",
                            task["id"], task.get("created_at", "?"), task["name"],
                            task["board_id"], task["column"])
                run_agent(config, task)
            elif not synced:
                log.info("[Pipe] Nenhuma tarefa elegível")
                log.info("[Pipe] intervalo: %ds", sleeptime)
                _log_wake(sleeptime)
                time.sleep(sleeptime)
        except RateLimitError:
            log.warning("[Pipe] Rate limit — dormindo %ds", sleeptime)
            _log_wake(sleeptime)
            time.sleep(sleeptime)
        except GitHubError as e:
            log.error("[Pipe] Erro GitHub: %s", e)
        except Exception as e:
            log.error("[Pipe] Erro inesperado: %s", e, exc_info=True)
            _log_wake(sleeptime)
            time.sleep(sleeptime)


if __name__ == "__main__":
    main()
