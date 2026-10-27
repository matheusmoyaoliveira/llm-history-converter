import json
import zipfile
from datetime import datetime
from pathlib import Path

from llm_history_converter.adapters.claude_cards import render_card
from llm_history_converter.models import Conversation, Message

SOURCE = "claude"
AUTHORS = {"human": "user", "assistant": "assistant"}
CONVERSATIONS_FILE = "conversations.json"

def _parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _block_text(block: dict) -> str:
    if block.get("type") == "text":
        return block.get("text", "")
    if block.get("type") == "tool_use":
        return render_card(block)
    return ""


def _message_text(raw: dict) -> str:
    blocks = raw.get("content")
    if not blocks:
        return raw.get("text", "")
    parts = [_block_text(b) for b in blocks]
    return "\n\n".join(p for p in parts if p)


def _to_message(raw: dict) -> Message:
    return Message(
        author=AUTHORS.get(raw["sender"], raw["sender"]),
         text=_message_text(raw),
        sent_at=_parse_date(raw["created_at"]),
    )


def _to_conversation(raw: dict) -> Conversation:
    return Conversation(
        id=raw["uuid"],
        title=raw.get("name") or "(sem título)",
        summary=(raw.get("summary") or "").strip() or None,
        source=SOURCE,
        created_at=_parse_date(raw["created_at"]),
        updated_at=_parse_date(raw["updated_at"]),
        messages=[
            m for m in (_to_message(r) for r in raw.get("chat_messages", []))
            if m.text.strip()
        ],
    )

def _read_export(path: Path) -> str:
    if path.suffix != ".zip":
        return path.read_text(encoding="utf-8")
    if path.name.startswith("conversations-"):
        parts = list(path.parent.glob("conversations-*.zip"))
        if len(parts) > 1:
            raise ValueError(
                f"o export está dividido em {len(parts)} arquivos conversations-*.zip, "
                "e isso ainda não é suportado"
            )
    try:
        with zipfile.ZipFile(path) as archive:
            if CONVERSATIONS_FILE not in archive.namelist():
                raise ValueError(f"{path.name} não tem o arquivo {CONVERSATIONS_FILE}")
            return archive.read(CONVERSATIONS_FILE).decode("utf-8")
    except zipfile.BadZipFile:
        raise ValueError(f"{path.name} não é um arquivo zip válido") from None


def load(path: Path) -> list[Conversation]:
    data = json.loads(_read_export(path))
    return [_to_conversation(item) for item in data]