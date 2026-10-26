from pathlib import Path

from llm_history_converter.cli import build_parser, format_summary


def test_summary_uses_singular_for_one():
    counts = {"new": 1, "updated": 1, "unchanged": 128}
    assert format_summary(counts) == "1 nova, 1 atualizada, 128 sem mudança"


def test_summary_uses_plural_for_many():
    counts = {"new": 129, "updated": 2, "unchanged": 0}
    assert format_summary(counts) == "129 novas, 2 atualizadas, 0 sem mudança"


def test_paths_starting_with_tilde_point_to_home():
    args = build_parser().parse_args(["claude", "~/export/conversations.json", "~/saida"])
    assert args.input == Path.home() / "export" / "conversations.json"
    assert args.output == Path.home() / "saida"


def test_paths_without_tilde_are_kept():
    args = build_parser().parse_args(["claude", "export/conversations.json", "saida"])
    assert args.input == Path("export/conversations.json")
    assert args.output == Path("saida")
