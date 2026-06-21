import time
from datetime import datetime, timezone, timedelta

from src.config import load_config
from src.log import log, cleanup_logs, set_level
from src.sync import sync, full_sync, _load_snapshot, _save_snapshot
from src.issues import sync_issues, sync_issues_local
from src.pick_task import pick_task, TODO_ADVANCE
from src.agent import run_agent
from src.github import (
    RateLimitError, GitHubError, sleep_until_rate_limit_reset,
    get_graphql_rate_info, configure as configure_github,
    is_in_penalty, penalty_remaining,
)

_tz = timezone(timedelta(hours=-3))


def _log_wake(sleeptime):
    wake = datetime.now(_tz) + timedelta(seconds=sleeptime)
    log.info("[Sleep Time] Retorno às %s", wake.strftime("%H:%M:%S"))


def main():
    log.info("")
    log.info("[Pipe] Inicianda")
    config = load_config("pipe.yml")
    set_level(config.get("pipe", {}).get("log", {}).get("level", "INFO"))
    cleanup_logs(config.get("ttl-log", 10))
    configure_github(config)

    # sync() roda apenas uma vez ao iniciar
    snapshot = sync(config)

    sleeptime = config["pipe"].get("sleeptime", 1800)

    # Full sync na inicialização — garante estado correto (pula se em penalty)
    if is_in_penalty():
        log.info("[Pipe] Penalty ativo — pulando full sync inicial")
    else:
        log.info("[Pipe] Full sync inicial")
        try:
            full_sync(config, snapshot)
        except RateLimitError as e:
            if is_in_penalty():
                log.info("[Pipe] Penalty ativado durante full sync — entrando em modo local")
            else:
                log.info("[Pipe] Throttle no full sync inicial — aguardando")
                sleep_until_rate_limit_reset(sleeptime, retry_after=e.retry_after)
                full_sync(config, snapshot)

    current_day = datetime.now(timezone.utc).date()
    log.info("[Pipe] Loop iniciado (dia: %s)", current_day)
    while True:
        try:
            # Penalty box: só sync local + agentes
            if is_in_penalty():
                sync_issues_local(config)
                task = pick_task(config)
                if task == TODO_ADVANCE:
                    log.info("[Pipe] Auto-advance realizado — aguardando sync propagar")
                elif task:
                    log.info("[Pipe] Tarefa selecionada: #%s [%s] %s (board: %s, col: %s)",
                                task["id"], task.get("created_at", "?"), task["name"],
                                task["board_id"], task["column"])
                    run_agent(config, task)
                else:
                    remaining = penalty_remaining()
                    log.info("[Pipe] Penalty ativo — restam %ds — nenhuma tarefa elegível", remaining)
                    _log_wake(sleeptime)
                    time.sleep(sleeptime)
                continue

            # Fluxo normal: virada de dia + sync completo
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
        except RateLimitError as e:
            if is_in_penalty():
                log.info("[Pipe] Penalty ativado — entrando em modo local")
                continue
            if e.retry_after:
                log.info("[Pipe] Throttle — aguardando API")
            else:
                log.warning("[Pipe] Rate limit — aguardando reset")
            sleep_until_rate_limit_reset(sleeptime, retry_after=e.retry_after)
            rate = get_graphql_rate_info()
            if rate:
                log.info("[Pipe] Rate info — remaining: %s, resetAt: %s", rate.get("remaining"), rate.get("resetAt"))
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
