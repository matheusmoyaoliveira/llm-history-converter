import argparse
import sys
from pathlib import Path

from llm_history_converter.adapters import claude
from llm_history_converter.state import classify, load_state, missing_ids, save_state, state_key
from llm_history_converter.writer import write

ADAPTERS = {"claude": claude.load}


def _count(value: int, singular: str, plural: str) -> str:
    return f"{value} {singular if value == 1 else plural}"


def format_summary(counts: dict[str, int]) -> str:
    return (
        f"{_count(counts['new'], 'nova', 'novas')}, "
        f"{_count(counts['updated'], 'atualizada', 'atualizadas')}, "
        f"{counts['unchanged']} sem mudança"
    )


def format_missing(ids: list[str]) -> str:
    if len(ids) == 1:
        header = "1 conversa do estado não está neste export (o arquivo dela foi mantido):"
    else:
        header = f"{len(ids)} conversas do estado não estão neste export (os arquivos delas foram mantidos):"
    return "\n".join([header] + [f"- {conversation_id[:8]}" for conversation_id in ids])


def _path(value: str) -> Path:
    return Path(value).expanduser()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Converte exports de chats de IA em arquivos Markdown."
    )
    parser.add_argument("source", choices=ADAPTERS.keys(), help="De onde veio o export")
    parser.add_argument("input", type=_path, help="Arquivo do export: conversations.json ou conversations-000.zip")
    parser.add_argument("output", type=_path, help="Pasta onde os arquivos serão gravados")
    parser.add_argument("--full", action="store_true", help="Ignora o estado e converte tudo de novo")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    try:
        conversations = ADAPTERS[args.source](args.input)
    except (OSError, ValueError) as error:
        sys.exit(f"Erro: {error}")
    state = {} if args.full else load_state(args.output)
    missing = missing_ids(state, args.source, conversations)
    counts = {"new": 0, "updated": 0, "unchanged": 0}
    for conversation in conversations:
        status = classify(conversation, state)
        counts[status] += 1
        if status == "unchanged":
            continue
        write(conversation, args.output)
        state[state_key(conversation)] = conversation.updated_at.isoformat()
    save_state(state, args.output)

    print(format_summary(counts))
    if missing:
        print(format_missing(missing))


if __name__ == "__main__":
    main()