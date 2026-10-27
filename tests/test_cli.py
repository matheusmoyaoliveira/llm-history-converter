import json
from pathlib import Path

import pytest

from llm_history_converter.cli import build_parser, format_summary, main


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


def test_missing_input_shows_clear_error(tmp_path):
    with pytest.raises(SystemExit) as error:
        main(["claude", str(tmp_path / "nao-existe.json"), str(tmp_path / "saida")])
    assert str(error.value).startswith("Erro: ")
    assert not (tmp_path / "saida").exists()


FIXTURE = Path(__file__).parent / "fixtures" / "claude_sample.json"


def _run_with_extra_state(tmp_path, capsys, *extra_args):
    output = tmp_path / "saida"
    main(["claude", str(FIXTURE), str(output)])
    state = json.loads((output / ".state.json").read_text(encoding="utf-8"))
    state["claude:12345678-sumiu"] = "2026-10-01T00:00:00+00:00"
    (output / ".state.json").write_text(json.dumps(state), encoding="utf-8")
    capsys.readouterr()
    main(["claude", str(FIXTURE), str(output), *extra_args])
    return capsys.readouterr().out


def test_warns_about_conversations_missing_from_export(tmp_path, capsys):
    out = _run_with_extra_state(tmp_path, capsys)
    assert "1 conversa do estado não está neste export" in out
    assert "- 12345678" in out


def test_missing_conversation_stays_in_state(tmp_path, capsys):
    _run_with_extra_state(tmp_path, capsys)
    state = json.loads((tmp_path / "saida" / ".state.json").read_text(encoding="utf-8"))
    assert "claude:12345678-sumiu" in state


def test_full_run_skips_missing_check(tmp_path, capsys):
    out = _run_with_extra_state(tmp_path, capsys, "--full")
    assert "não está neste export" not in out


def test_no_warning_when_nothing_is_missing(tmp_path, capsys):
    main(["claude", str(FIXTURE), str(tmp_path)])
    main(["claude", str(FIXTURE), str(tmp_path)])
    assert "neste export" not in capsys.readouterr().out
