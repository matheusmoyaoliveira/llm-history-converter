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

On Windows PowerShell, activate the virtual environment with `.venv\Scripts\Activate.ps1` instead.

## Usage

```bash
llm-history-converter claude path/to/conversations-000.zip path/to/output
```

- `claude` is the source of the export.
- The input can be the `conversations-000.zip` file from the export, read directly without unzipping, or the `conversations.json` inside it. Exports split into several `conversations-*.zip` files are not supported yet.
- The output folder is created if it does not exist.
- Paths may start with `~` for your home folder, in any shell (Git Bash, PowerShell, Linux or macOS), for example `~/exports/conversations.json`.

Runs are incremental. The tool keeps a `.state.json` file in the output folder with the last update time of each conversation, and on the next run it only writes conversations that are new or were updated since then. At the end it prints a summary (the CLI messages are in Portuguese):

```text
3 novas, 2 atualizadas, 40 sem mudança
```

That is 3 new, 2 updated and 40 unchanged conversations. If the state has conversations that are not in the current export (the Claude export sometimes leaves conversations out), the tool lists the first 8 characters of their ids. Their Markdown files are kept.

To ignore the state and convert everything again, use `--full`:

```bash
llm-history-converter claude path/to/conversations-000.zip path/to/output --full
```

### Output

Each conversation becomes a file named `<creation date> - <first 8 chars of the id>.md`, with the metadata in the frontmatter and dates shown in your local timezone. When the export has a summary of the conversation, it goes right after the title, in a collapsed Obsidian callout (a plain quote in other Markdown viewers):

```markdown
---
id: 3f2a9c1e-0000-0000-0000-000000000000
fonte: claude
criada_em: 2026-01-10T14:00:00+00:00
atualizada_em: 2026-01-10T14:05:00+00:00
---

# Planning a trip

> [!summary]- Resumo
> The user asked what to pack for a weekend trip.

## Você — 10/01/2026 11:00

What should I pack for a weekend in the mountains?

## IA — 10/01/2026 11:01

Layers, a rain jacket and comfortable shoes.
```

## Architecture

```text
src/llm_history_converter/
├── models.py      # common model: Conversation and Message
├── adapters/      # one adapter per source (claude.py, plus claude_cards.py)
├── writer.py      # turns a Conversation into a Markdown file
├── state.py       # incremental state (.state.json)
└── cli.py         # the llm-history-converter command
```

- **Common model:** every source is translated into the same `Conversation` and `Message` dataclasses, so the rest of the code does not depend on any export format.
- **Adapters:** each source has a module with a `load(path)` function that returns a list of `Conversation`. The Claude adapter keeps text blocks, turns display cards (step-by-step guides, questions, message drafts, options, comparisons, links, quizzes and charts) into Markdown with `claude_cards.py`, and skips messages that end up empty. Adding a source means adding an adapter and registering it in `cli.py`.
- **Writer:** builds the Markdown (frontmatter plus messages) and saves the file.
- **State:** stores the `updated_at` of each conversation under a `source:id` key and classifies each conversation as new, updated or unchanged. A conversation counts as updated only if its `updated_at` is later than the stored one, so running an older export after a newer one rewrites nothing.

## Running the tests

```bash
pytest
```

The tests use a small fictional export in `tests/fixtures/` and pytest's temporary folders. No real data is needed.

## Known limitations

- **Missing conversations:** the Claude export leaves some conversations out, so they cannot be converted.
- **Tool calls:** display cards are converted, but other tool calls (running commands, web searches, file edits) and their results are left out, as are thinking blocks, images and attached documents.
- **Edited messages:** when a message is edited or a response is regenerated, the conversation branches. Only the latest branch is kept (the path from the first message to the most recent one, which is the version you saw last); earlier versions are dropped.
- **Projects:** the export does not link conversations to the projects they belong to, so the output has no project information.

## Roadmap

- ChatGPT adapter.
