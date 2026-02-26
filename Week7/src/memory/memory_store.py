import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class MemoryStore:
    """
    Stores last N messages per session_id and writes them to src/logs/CHAT-LOGS.json.
    """

    def __init__(self, keep_last: int = 5, log_path: str = "src/logs/CHAT-LOGS.json"):
        self.keep_last = keep_last
        self.log_file = Path(log_path)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.sessions: Dict[str, list] = {}
        self._load_existing()

    def _load_existing(self) -> None:
        if not self.log_file.exists():
            self.sessions = {}
            return
        try:
            self.sessions = json.loads(self.log_file.read_text(encoding="utf-8"))
            if not isinstance(self.sessions, dict):
                self.sessions = {}
        except Exception:
            self.sessions = {}

    def add(self, sid: str, role: str, text: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if sid not in self.sessions:
            self.sessions[sid] = []

        msg = {
            "time": datetime.now().isoformat(),
            "role": role,
            "text": text,
            "meta": meta or {},
        }

        self.sessions[sid].append(msg)

        # keep last N only
        if len(self.sessions[sid]) > self.keep_last:
            self.sessions[sid] = self.sessions[sid][-self.keep_last :]

        self.save()
        return msg

    def get(self, sid: str) -> list:
        return self.sessions.get(sid, [])

    def save(self) -> None:
        self.log_file.write_text(json.dumps(self.sessions, indent=2), encoding="utf-8")


# singleton (import this everywhere)
memory = MemoryStore(keep_last=5)