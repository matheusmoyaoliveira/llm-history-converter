import argparse
from pathlib import Path

from llm_history_converter.adapters import claude
from llm_history_converter.state import classify, load_state, save_state, state_key
from llm_history_converter.writer import write

ADAPTERS = {"claude": claude.load}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Converte exports de chats de IA em arquivos Markdown."
    )
    parser.add_argument("source", choices=ADAPTERS.keys(), help="De onde veio o export")
    parser.add_argument("input", type=Path, help="Arquivo do export, como conversations.json")
    parser.add_argument("output", type=Path, help="Pasta onde os arquivos serão gravados")
    parser.add_argument("--full", action="store_true", help="Ignora o estado e converte tudo de novo")
    args = parser.parse_args()

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

    print(
        f"{counts['new']} novas, {counts['updated']} atualizadas, "
        f"{counts['unchanged']} sem mudança"
    )


if __name__ == "__main__":
    main()