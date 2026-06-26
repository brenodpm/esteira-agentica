"""Board core - gerencia boards via port."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from src.core.log import log


class PenaltyException(Exception):
    """Rate limit atingido - aguardar antes de tentar novamente."""
    def __init__(self, wait_seconds: int):
        self.wait_seconds = wait_seconds
        super().__init__(f"Rate limit - aguardar {wait_seconds}s")


class SyncEvent(str, Enum):
    """Evento de sincronismo registrado na fila de mudanças.

    Sufixo '-up' = origem local (precisa subir para o board).
    Sufixo '-down' = origem no board (precisa descer para o local).
    """
    CREATE_UP = "create-up"      # criado localmente
    CREATE_DOWN = "create-down"  # criado no board
    CHANGE_UP = "change-up"      # modificado localmente
    CHANGE_DOWN = "change-down"  # modificado no board
    DELETE_UP = "delete-up"      # deletado localmente
    DELETE_DOWN = "delete-down"  # deletado no board


@dataclass
class ChangeItem:
    """Item da fila de sincronismo (.pipe/changeQueue.json)."""
    timestamp: str       # horário em que foi adicionado na fila (ISO 8601 UTC)
    event: str           # SyncEvent
    id: str = None       # id da issue no board (None quando ainda não existe)
    identifier: str = None  # identificador local enquanto não há id de board
    board: str = None       # board_id ao qual a issue pertence
    uuid: str = None        # id único na fila (atribuído por add/addAll)

    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @classmethod
    def of(cls, event, id: str = None, identifier: str = None,
           board: str = None) -> "ChangeItem":
        """Cria um ChangeItem com timestamp atual."""
        return cls(
            timestamp=cls.now(),
            event=event.value if isinstance(event, SyncEvent) else event,
            id=id,
            identifier=identifier,
            board=board,
        )

    def same_target(self, other: "ChangeItem") -> bool:
        """True se representa o mesmo alvo de sincronismo (para deduplicação).

        Considera duplicado quando event, id, identifier e board são iguais.
        """
        return (
            self.event == other.event
            and self.id == other.id
            and self.identifier == other.identifier
            and self.board == other.board
        )


@dataclass
class Issue:
    id: str
    title: str
    body: str
    column: str
    labels: list[str] = None
    updated_at: str = None


class BoardPort(ABC):
    """Port para adapters de board (GitHub, ClickUp, etc)."""

    @abstractmethod
    def connect(self, config: dict) -> None:
        """Conecta ao serviço."""
        pass

    @abstractmethod
    def sync_boards(self, boards: list[dict]) -> None:
        """Sincroniza estrutura de boards e colunas."""
        pass

    @abstractmethod
    def list_issues(self, board_id: str) -> list[Issue]:
        """Lista issues de um board."""
        pass

    @abstractmethod
    def get_issue(self, board_id: str, issue_id: str) -> Issue:
        """Busca uma issue específica."""
        pass

    @abstractmethod
    def move_issue(self, board_id: str, issue_id: str, column: str) -> None:
        """Move issue para outra coluna."""
        pass

    @abstractmethod
    def update_issue(self, board_id: str, issue_id: str, title: str = None, body: str = None) -> None:
        """Atualiza título e/ou body da issue."""
        pass

    @abstractmethod
    def add_comment(self, board_id: str, issue_id: str, comment: str) -> None:
        """Adiciona comentário na issue."""
        pass


class Board:
    """Core de boards - usa port para operações."""

    def __init__(self, port: BoardPort):
        self._port = port

    def connect(self, config: dict):
        self._port.connect(config)

    def sync_boards(self, config: dict):
        """Extrai boards do config e sincroniza via port."""
        boards = []
        for board_id, board_cfg in config.get("boards", {}).items():
            if board_id == "platform":
                continue
            columns = list(board_cfg.get("columns", {}).keys())
            boards.append({
                "id": board_id,
                "name": board_cfg.get("name"),
                "columns": columns
            })
        # Ordena por prioridade
        boards.sort(key=lambda b: config["boards"][b["id"]].get("priority", 999))
        self._port.sync_boards(boards)

    def list_issues(self, board_id: str) -> list[Issue]:
        return self._port.list_issues(board_id)

    def get_issue(self, board_id: str, issue_id: str) -> Issue:
        return self._port.get_issue(board_id, issue_id)

    def move_issue(self, board_id: str, issue_id: str, column: str):
        self._port.move_issue(board_id, issue_id, column)

    def update_issue(self, board_id: str, issue_id: str, title: str = None, body: str = None):
        self._port.update_issue(board_id, issue_id, title, body)

    def add_comment(self, board_id: str, issue_id: str, comment: str):
        self._port.add_comment(board_id, issue_id, comment)

    def board_ids(self, config: dict) -> list[str]:
        """Retorna os ids dos boards configurados (ignora 'platform')."""
        return [bid for bid in config.get("boards", {}) if bid != "platform"]

    def detect_board_changes(self, board_id: str, snapshot, queue) -> int:
        """Detecta mudanças de um board comparando com o snapshot e registra na fila.

          - issue no board sem correspondência no snapshot  -> create-down
          - issue no snapshot (com id) ausente no board      -> delete-down
          - issue com updated_at no board > snapshot         -> change-down

        Não sincroniza nada: apenas enfileira os eventos em ChangeQueue.
        A única chamada de API é list_issues; a detecção é feita em memória.
        A deduplicação fica a cargo da fila (addAll).
        Retorna a quantidade de itens efetivamente adicionados à fila.
        """
        remote_issues = self._port.list_issues(board_id)
        remote_by_id = {str(i.id): i for i in remote_issues}

        snapshot_issues = snapshot.issues
        snapshot_by_id = {
            str(i["id"]): i for i in snapshot_issues if i.get("id") is not None
        }

        changes: list[ChangeItem] = []

        # Criadas ou modificadas no board
        for issue in remote_issues:
            issue_id = str(issue.id)
            known = snapshot_by_id.get(issue_id)

            if known is None:
                changes.append(ChangeItem.of(SyncEvent.CREATE_DOWN, id=issue_id, board=board_id))
                continue

            remote_at = issue.updated_at or ""
            snap_at = known.get("updated_at") or ""
            if remote_at and snap_at and remote_at > snap_at:
                changes.append(ChangeItem.of(SyncEvent.CHANGE_DOWN, id=issue_id, board=board_id))

        # Deletadas no board (existiam no snapshot com id, sumiram do board)
        for issue_id in snapshot_by_id:
            if issue_id not in remote_by_id:
                changes.append(ChangeItem.of(SyncEvent.DELETE_DOWN, id=issue_id, board=board_id))

        return queue.addAll(changes)
