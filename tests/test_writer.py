from datetime import datetime, timezone

from llm_history_converter.models import Conversation
from llm_history_converter.writer import to_markdown

DATE = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)


def _conversation(summary: str | None) -> Conversation:
    return Conversation(
        id="abc", title="Teste", source="claude", created_at=DATE, updated_at=DATE, summary=summary
    )


def test_summary_goes_right_after_title_as_collapsed_callout():
    markdown = to_markdown(_conversation("**Visão geral**\n\nPrimeira linha"))
    assert "# Teste\n\n> [!summary]- Resumo\n> **Visão geral**\n>\n> Primeira linha\n" in markdown


def test_no_summary_means_no_callout():
    assert "[!summary]" not in to_markdown(_conversation(None))
