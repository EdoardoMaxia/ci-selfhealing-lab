def deduplicate_preserves_first(items):
    """Rimuove i duplicati preservando l'ordine di prima apparizione."""
    seen = dict.fromkeys(items)
    return list(seen)
