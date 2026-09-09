from src.logger import log_entry


def test_second_call_has_only_its_own_entries():
    result1 = log_entry("first")
    result2 = log_entry("second")
    assert result2 == ["second"]