def recommend(items):
    """items: lista di dict con 'id' e 'score'. Ordina per punteggio decrescente,
    a parità di punteggio ordina per 'id' crescente (tie-break deterministico)."""
    return [i["id"] for i in sorted(items, key=lambda x: (-x["score"], x["id"]))]
