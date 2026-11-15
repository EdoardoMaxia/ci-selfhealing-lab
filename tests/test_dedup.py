from src.dedup import deduplicate_preserves_first


def test_deduplicate_preserves_first():
    result = deduplicate_preserves_first(["b", "a", "b", "c"])
    assert result == ["b", "a", "c"]