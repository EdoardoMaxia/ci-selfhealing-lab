from src.logger import log_entry

def test_second_call_has_only_its_own_entries():
    log_entry("first")
    result1 = log_entry("second")
    log_entry("third")
    result2 = log_entry("second")
    assert result1 not in result2
    assert result2 == ["second"]