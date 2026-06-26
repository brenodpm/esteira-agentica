"""Snapshot core - estado conhecido das issues entre execuções.

Persiste em .pipe/snapshot.json o último estado sincronizado de cada board.
Usado para comparar com o estado remoto e detectar mudanças.

Estrutura:
{
  "issues": {
    "<board_id>": [
      {"id": "<board_id_da_issue>", "updated_at": "<ISO 8601>", ...}
    ]
  }
}
"""

import json
from pathlib import Path

PIPE_DIR = Path(".pipe")
SNAPSHOT_FILE = PIPE_DIR / "snapshot.json"


class Snapshot:
    """Estado conhecido das issues, persistido entre execuções."""

    def __init__(self):
        self._data: dict = {"issues": {}}

    def load(self) -> "Snapshot":
        """Carrega o snapshot do disco (vazio se o arquivo não existir)."""
        if SNAPSHOT_FILE.exists():
            self._data = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
            self._data.setdefault("issues", {})
        else:
            self._data = {"issues": {}}
        return self

    def save(self) -> None:
        """Persiste o snapshot no disco."""
        PIPE_DIR.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_FILE.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def issues(self, board_id: str) -> list[dict]:
        """Retorna as issues conhecidas de um board."""
        return self._data.get("issues", {}).get(board_id, [])

    def issue(self, board_id: str, issue_id: str) -> dict | None:
        """Busca uma issue específica pelo id no board."""
        for issue in self.issues(board_id):
            if str(issue.get("id")) == str(issue_id):
                return issue
        return None
