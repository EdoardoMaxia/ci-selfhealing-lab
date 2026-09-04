def log_entry(entry, entries=None):
    if entries is None:
        entries = []
    entries.append(entry)
    return entries