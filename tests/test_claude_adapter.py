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

CARDS_FIXTURE = Path(__file__).parent / "fixtures" / "claude_cards_sample.json"


def test_card_appears_between_text_blocks():
    message = load(CARDS_FIXTURE)[0].messages[1]
    assert message.text == (
        "Siga estes passos:\n"
        "\n"
        "**Passo a passo:** Publicar o site\n"
        "\n"
        "1. **Gerar o build**\n"
        "   Rode npm run build.\n"
        "\n"
        "Qualquer dúvida, me chame."
    )


def test_card_only_message_is_kept():
    messages = load(CARDS_FIXTURE)[0].messages
    assert len(messages) == 4
    assert messages[2].text == "**Pergunta:** Seguimos?\n- Sim\n- Não"


def test_regular_tool_blocks_are_ignored():
    assert load(CARDS_FIXTURE)[0].messages[3].text == "Pronto."


def test_reads_conversation_summary():
    assert load(FIXTURE)[0].summary == "**Conversation overview**\nO usuário pediu ajuda com um teste."


def test_empty_summary_becomes_none():
    assert load(FIXTURE)[1].summary is None
