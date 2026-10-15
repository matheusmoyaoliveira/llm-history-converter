import json
from datetime import datetime
from pathlib import Path

from llm_history_converter.models import Conversation, Message

SOURCE = "claude"
AUTHORS = {"human": "user", "assistant": "assistant"}

def _parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _to_message(raw: dict) -> Message:
    return Message(
        author=AUTHORS.get(raw["sender"], raw["sender"]),
        text=raw.get("text", ""),
        sent_at=_parse_date(raw["created_at"]),
    )


def _to_conversation(raw: dict) -> Conversation:
    return Conversation(
        id=raw["uuid"],
        title=raw.get("name") or "(sem título)",
        source=SOURCE,
        created_at=_parse_date(raw["created_at"]),
        updated_at=_parse_date(raw["updated_at"]),
        messages=[_to_message(m) for m in raw.get("chat_messages", [])],
    )

def load(path: Path) -> list[Conversation]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [_to_conversation(item) for item in data]