from datetime import datetime, timezone

from llm_history_converter.models import Conversation
from llm_history_converter.state import classify, load_state, missing_ids, save_state, state_key

OLD = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)
NEW = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc)


def _conversation(updated_at: datetime) -> Conversation:
    return Conversation(
        id="abc", title="Teste", source="claude", created_at=OLD, updated_at=updated_at
    )


def test_unknown_conversation_is_new():
    assert classify(_conversation(OLD), {}) == "new"


def test_same_date_is_unchanged():
    state = {"claude:abc": OLD.isoformat()}
    assert classify(_conversation(OLD), state) == "unchanged"


def test_later_date_is_updated():
    state = {"claude:abc": OLD.isoformat()}
    assert classify(_conversation(NEW), state) == "updated"


def test_missing_state_file_returns_empty(tmp_path):
    assert load_state(tmp_path) == {}


def test_saved_state_can_be_loaded(tmp_path):
    state = {state_key(_conversation(OLD)): OLD.isoformat()}
    save_state(state, tmp_path)
    assert load_state(tmp_path) == state


def test_conversation_absent_from_export_is_missing():
    state = {"claude:abc": OLD.isoformat(), "claude:xyz": OLD.isoformat()}
    assert missing_ids(state, "claude", [_conversation(OLD)]) == ["xyz"]


def test_nothing_missing_when_export_has_everything():
    state = {"claude:abc": OLD.isoformat()}
    assert missing_ids(state, "claude", [_conversation(OLD)]) == []


def test_other_sources_are_not_missing():
    state = {"claude:abc": OLD.isoformat(), "chatgpt:xyz": OLD.isoformat()}
    assert missing_ids(state, "claude", [_conversation(OLD)]) == []
