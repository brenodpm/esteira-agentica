import time
from datetime import datetime, timezone, timedelta

from src.config import load_config
from src.log import log, cleanup_logs
from src.sync import sync, full_sync, _load_snapshot, _save_snapshot
from src.issues import sync_issues
from src.pick_task import pick_task, TODO_ADVANCE
from src.agent import run_agent
from src.github import RateLimitError, GitHubError, sleep_until_rate_limit_reset

_tz = timezone(timedelta(hours=-3))


def _log_wake(sleeptime):
    wake = datetime.now(_tz) + timedelta(seconds=sleeptime)
    log.info("[Sleep Time] Retorno às %s", wake.strftime("%H:%M:%S"))


def main():
    log.info("")
    log.info("[Pipe] Inicianda")
    config = load_config("pipe.yml")
    cleanup_logs(config.get("ttl-log", 10))

    # sync() roda apenas uma vez ao iniciar
    snapshot = sync(config)

    # Full sync na inicialização — garante estado correto
    log.info("[Pipe] Full sync inicial")
    full_sync(config, snapshot)

    sleeptime = config["pipe"].get("agent", {}).get("sleeptime", 5)
    current_day = datetime.now(timezone.utc).date()
    log.info("[Pipe] Loop iniciado (dia: %s)", current_day)
    while True:
        try:
            # Detectar virada REAL de dia (meia-noite UTC passou)
            today = datetime.now(timezone.utc).date()
            if today > current_day:
                log.info("[Pipe] Virada de dia detectada (%s → %s) — full sync", current_day, today)
                snapshot = _load_snapshot()
                full_sync(config, snapshot)
                current_day = today

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
            log.warning("[Pipe] Rate limit — consultando reset time")
            sleep_until_rate_limit_reset()
        except GitHubError as e:
            log.error("[Pipe] Erro GitHub: %s", e)
            _log_wake(sleeptime)
            time.sleep(sleeptime)
        except Exception as e:
            log.error("[Pipe] Erro inesperado: %s", e, exc_info=True)
            _log_wake(sleeptime)
            time.sleep(sleeptime)


if __name__ == "__main__":
    main()
