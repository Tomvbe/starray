from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
import json
from pathlib import Path
from uuid import uuid4


@dataclass(slots=True)
class SessionState:
    session_id: str
    created_at: str
    turns: list[dict[str, str]] = field(default_factory=list)

    @classmethod
    def new(cls) -> "SessionState":
        return cls(
            session_id=uuid4().hex,
            created_at=datetime.now(UTC).isoformat(),
            turns=[],
        )

    def add_turn(self, role: str, content: str) -> None:
        self.turns.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "role": role,
                "content": content,
            }
        )

    def save(self, session_dir: Path) -> Path:
        session_dir.mkdir(parents=True, exist_ok=True)
        path = session_dir / f"{self.session_id}.json"
        payload = {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "turns": self.turns,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path


class SessionError(RuntimeError):
    """Raised when loading a session fails."""


def load_session(session_dir: Path, session_id: str) -> SessionState:
    path = session_dir / f"{session_id}.json"
    if not path.exists():
        raise SessionError(f"Session not found: {session_id}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SessionError(f"Session file is invalid JSON: {path}") from exc

    return SessionState(
        session_id=payload["session_id"],
        created_at=payload["created_at"],
        turns=list(payload.get("turns", [])),
    )
