import json
from datetime import datetime
from pathlib import Path

from llm_history_converter.models import Conversation

STATE_FILE = ".state.json"


def state_key(conversation: Conversation) -> str:
    return f"{conversation.source}:{conversation.id}"


def load_state(folder: Path) -> dict[str, str]:
    path = folder / STATE_FILE
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(state: dict[str, str], folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / STATE_FILE).write_text(json.dumps(state, indent=2), encoding="utf-8")


def classify(conversation: Conversation, state: dict[str, str]) -> str:
    saved = state.get(state_key(conversation))
    if saved is None:
        return "new"
    if conversation.updated_at > datetime.fromisoformat(saved):
        return "updated"
    return "unchanged"
