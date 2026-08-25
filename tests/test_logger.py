from src.logger import log_entry

def test_second_call_has_only_its_own_entries():
    log_entry("first", entries=[])
    result2 = log_entry("second", entries=[])
    assert result2 == ["second"]