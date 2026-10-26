import argparse
from pathlib import Path

from llm_history_converter.adapters import claude
from llm_history_converter.state import classify, load_state, save_state, state_key
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


def _path(value: str) -> Path:
    return Path(value).expanduser()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Converte exports de chats de IA em arquivos Markdown."
    )
    parser.add_argument("source", choices=ADAPTERS.keys(), help="De onde veio o export")
    parser.add_argument("input", type=_path, help="Arquivo do export, como conversations.json")
    parser.add_argument("output", type=_path, help="Pasta onde os arquivos serão gravados")
    parser.add_argument("--full", action="store_true", help="Ignora o estado e converte tudo de novo")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    conversations = ADAPTERS[args.source](args.input)
    state = {} if args.full else load_state(args.output)
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


if __name__ == "__main__":
    main()