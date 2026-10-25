# llm-history-converter

Converts AI chat exports into Markdown files, one file per conversation.

AI chat apps let you export your history, but the export is one large JSON file that is hard to read, search or link to. This tool turns it into plain Markdown files, ready for a notes app such as Obsidian. Today it reads the Claude export; a ChatGPT adapter is on the roadmap.

## Installation

Requires Python 3.12 or newer.

```bash
git clone https://github.com/matheusmoyaoliveira/llm-history-converter.git
cd llm-history-converter
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash); on Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
llm-history-converter claude path/to/conversations.json path/to/output
```

- `claude` is the source of the export.
- `conversations.json` is the file inside the export zip.
- The output folder is created if it does not exist.

Runs are incremental. The tool keeps a `.state.json` file in the output folder with the last update time of each conversation, and on the next run it only writes conversations that are new or were updated since then. At the end it prints a summary (the CLI messages are in Portuguese):

```text
3 novas, 2 atualizadas, 40 sem mudança
```

That is 3 new, 2 updated and 40 unchanged conversations. To ignore the state and convert everything again, use `--full`:

```bash
llm-history-converter claude path/to/conversations.json path/to/output --full
```

### Output

Each conversation becomes a file named `<creation date> - <first 8 chars of the id>.md`, with the metadata in the frontmatter and dates shown in your local timezone:

```markdown
---
id: 3f2a9c1e-0000-0000-0000-000000000000
fonte: claude
criada_em: 2026-01-10T14:00:00+00:00
atualizada_em: 2026-01-10T14:05:00+00:00
---

# Planning a trip

## Você — 10/01/2026 11:00

What should I pack for a weekend in the mountains?

## IA — 10/01/2026 11:01

Layers, a rain jacket and comfortable shoes.
```

## Architecture

```text
src/llm_history_converter/
├── models.py      # common model: Conversation and Message
├── adapters/      # one adapter per source (claude.py)
├── writer.py      # turns a Conversation into a Markdown file
├── state.py       # incremental state (.state.json)
└── cli.py         # the llm-history-converter command
```

- **Common model:** every source is translated into the same `Conversation` and `Message` dataclasses, so the rest of the code does not depend on any export format.
- **Adapters:** each source has a module with a `load(path)` function that returns a list of `Conversation`. The Claude adapter keeps only text blocks and skips messages that end up empty. Adding a source means adding an adapter and registering it in `cli.py`.
- **Writer:** builds the Markdown (frontmatter plus messages) and saves the file.
- **State:** stores the `updated_at` of each conversation under a `source:id` key and classifies each conversation as new, updated or unchanged. A conversation counts as updated only if its `updated_at` is later than the stored one, so running an older export after a newer one rewrites nothing.

## Running the tests

```bash
pytest
```

The tests use a small fictional export in `tests/fixtures/` and pytest's temporary folders. No real data is needed.

## Known limitations

- **Missing conversations:** the Claude export leaves some conversations out, so they cannot be converted.
- **Tool cards:** the content of tool cards (such as step-by-step tool calls) is lost. Only text blocks are converted.
- **Edited messages:** when a message is edited, the conversation branches. Branches are not handled: all messages are written in the order they appear in the export.
- **Projects:** the export does not link conversations to the projects they belong to, so the output has no project information.

## Roadmap

- ChatGPT adapter.
