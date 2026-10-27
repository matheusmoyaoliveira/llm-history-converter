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


def missing_ids(state: dict[str, str], source: str, conversations: list[Conversation]) -> list[str]:
    current = {state_key(conversation) for conversation in conversations}
    prefix = f"{source}:"
    return sorted(
        key.removeprefix(prefix) for key in state if key.startswith(prefix) and key not in current
    )
