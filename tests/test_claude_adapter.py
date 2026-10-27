import zipfile
from pathlib import Path

import pytest

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


def _zip(path: Path, files: dict[str, str]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return path


def test_reads_conversations_from_zip(tmp_path):
    content = FIXTURE.read_text(encoding="utf-8")
    export = _zip(tmp_path / "conversations-000.zip", {"conversations.json": content})
    assert [c.id for c in load(export)] == [c.id for c in load(FIXTURE)]


def test_zip_without_conversations_file_fails_clearly(tmp_path):
    export = _zip(tmp_path / "conversations-000.zip", {"outro.json": "[]"})
    with pytest.raises(ValueError, match="não tem o arquivo conversations.json"):
        load(export)


def test_split_export_fails_clearly(tmp_path):
    export = _zip(tmp_path / "conversations-000.zip", {"conversations.json": "[]"})
    _zip(tmp_path / "conversations-001.zip", {"conversations.json": "[]"})
    with pytest.raises(ValueError, match="dividido em 2 arquivos"):
        load(export)


def test_invalid_zip_fails_clearly(tmp_path):
    export = tmp_path / "conversations-000.zip"
    export.write_text("não é zip", encoding="utf-8")
    with pytest.raises(ValueError, match="não é um arquivo zip válido"):
        load(export)


BRANCHES_FIXTURE = Path(__file__).parent / "fixtures" / "claude_branches_sample.json"


def test_edited_message_keeps_only_latest_branch():
    texts = [m.text for m in load(BRANCHES_FIXTURE)[0].messages]
    assert texts == [
        "Primeira pergunta",
        "Primeira resposta",
        "Pergunta editada",
        "Resposta à pergunta editada",
    ]


def test_conversation_without_edits_keeps_all_messages_in_order():
    texts = [m.text for m in load(BRANCHES_FIXTURE)[1].messages]
    assert texts == ["Olá", "Oi!", "Tudo bem?"]
