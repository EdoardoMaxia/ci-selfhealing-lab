def get_registry():
    """
    Registro plugin popolato nell'ordine di scoperta/registrazione (non
    alfabetico) — riflette un registro reale i cui elementi arrivano
    nell'ordine in cui i plugin vengono scoperti, non ordinati (per test_029).
    Deterministico: un dict Python preserva sempre l'ordine di inserimento
    (dal 3.7), a differenza di un set la cui iterazione dipende dall'hash
    randomizzato delle stringhe e sarebbe solo intermittentemente "sbagliata".
    """
    registry = {}
    registry["b_plugin"] = True
    registry["a_plugin"] = True
    return registry
