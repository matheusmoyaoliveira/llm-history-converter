import argparse
from pathlib import Path

from llm_history_converter.adapters import claude
from llm_history_converter.writer import write

ADAPTERS = {"claude": claude.load}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Converte exports de chats de IA em arquivos Markdown."
    )
    parser.add_argument("source", choices=ADAPTERS.keys(), help="De onde veio o export")
    parser.add_argument("input", type=Path, help="Arquivo do export, como conversations.json")
    parser.add_argument("output", type=Path, help="Pasta onde os arquivos serão gravados")
    args = parser.parse_args()

    conversations = ADAPTERS[args.source](args.input)
    for conversation in conversations:
        write(conversation, args.output)

    print(f"{len(conversations)} conversas convertidas em {args.output}")


if __name__ == "__main__":
    main()