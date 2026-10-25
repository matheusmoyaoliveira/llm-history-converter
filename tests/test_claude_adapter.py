from pathlib import Path

from llm_history_converter.adapters.claude import load

FIXTURE = Path(__file__).parent / "fixtures" / "claude_sample.json"


def test_loads_all_conversations():
    assert len(load(FIXTURE)) == 2


def test_translates_human_to_user():
    first_message = load(FIXTURE)[0].messages[0]
    assert first_message.author == "user"


def test_skips_tool_only_messages():
    assert len(load(FIXTURE)[0].messages) == 2


def test_keeps_only_text_blocks():
    second_message = load(FIXTURE)[0].messages[1]
    assert second_message.text == "Primeira parte\n\nSegunda parte"


def test_untitled_conversation_gets_default_title():
    assert load(FIXTURE)[1].title == "(sem título)"