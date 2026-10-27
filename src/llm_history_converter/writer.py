from pathlib import Path

from llm_history_converter.models import Conversation

AUTHOR_LABELS = {"user": "Você", "assistant": "IA"}


def _format_date(value) -> str:
    return value.astimezone().strftime("%d/%m/%Y %H:%M")


def to_markdown(conversation: Conversation) -> str:
    lines = [
        "---",
        f"id: {conversation.id}",
        f"fonte: {conversation.source}",
        f"criada_em: {conversation.created_at.isoformat()}",
        f"atualizada_em: {conversation.updated_at.isoformat()}",
        "---",
        "",
        f"# {conversation.title}",
        "",
    ]
    if conversation.summary:
        lines.append("> [!summary]- Resumo")
        lines += [f"> {line}".rstrip() for line in conversation.summary.splitlines()]
        lines.append("")
    for message in conversation.messages:
        label = AUTHOR_LABELS.get(message.author, message.author)
        lines.append(f"## {label} — {_format_date(message.sent_at)}")
        lines.append("")
        lines.append(message.text)
        lines.append("")
    return "\n".join(lines)

def _filename(conversation: Conversation) -> str:
    date = conversation.created_at.astimezone().strftime("%Y-%m-%d")
    return f"{date} - {conversation.id[:8]}.md"


def write(conversation: Conversation, folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / _filename(conversation)
    path.write_text(to_markdown(conversation), encoding="utf-8")
    return path