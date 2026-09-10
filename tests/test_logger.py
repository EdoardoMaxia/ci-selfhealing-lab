from src.logger import log_entry

def test_first_call():
    log_entry("first")
    entries = log_entry.call_args_list
    assert len(entries) == 1 and entries[0][0] == "first"

def test_second_call_has_only_its_own_entries():
    log_entry("first")
    log_entry.call_args_list.clear() # Clear the list before logging the second entry
    log_entry("second")
    entries = log_entry.call_args_list
    assert [entry[0] for entry in entries] == ['second']