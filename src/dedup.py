def deduplicate_preserves_first(items):
    """Removes duplicates while preserving the order of first appearance."""
    seen = dict.fromkeys(items)
    return list(seen)
