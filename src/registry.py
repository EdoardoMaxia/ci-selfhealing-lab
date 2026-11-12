def get_registry():
    """
    Plugin registry populated in discovery/registration order (not
    alphabetical) — mirrors a real registry whose items arrive
    in the order in which plugins are discovered, unsorted (for test_029).
    Deterministic: a Python dict always preserves insertion order
    (since 3.7), unlike a set whose iteration depends on the randomized
    string hash and would only be intermittently "wrong".
    """
    registry = {}
    registry["b_plugin"] = True
    registry["a_plugin"] = True
    return registry
