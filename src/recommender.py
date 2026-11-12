def recommend(items):
    """items: list of dicts with 'id' and 'score'. Sorts by descending score;
    on equal scores sorts by ascending 'id' (deterministic tie-break)."""
    return [i["id"] for i in sorted(items, key=lambda x: (-x["score"], x["id"]))]
