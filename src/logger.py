def log_entry(entry, entries=None):
    """Accoda entry a una lista indipendente per ogni chiamata (per test_049)."""
    entries = entries if entries is not None else []
    entries.append(entry)
    return entries
