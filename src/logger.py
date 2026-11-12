def log_entry(entry, entries=None):
    """Appends entry to an independent list on every call (for test_049)."""
    entries = entries if entries is not None else []
    entries.append(entry)
    return entries
