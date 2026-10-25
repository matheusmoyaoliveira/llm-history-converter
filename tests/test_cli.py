from llm_history_converter.cli import format_summary


def test_summary_uses_singular_for_one():
    counts = {"new": 1, "updated": 1, "unchanged": 128}
    assert format_summary(counts) == "1 nova, 1 atualizada, 128 sem mudança"


def test_summary_uses_plural_for_many():
    counts = {"new": 129, "updated": 2, "unchanged": 0}
    assert format_summary(counts) == "129 novas, 2 atualizadas, 0 sem mudança"
