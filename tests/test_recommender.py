from src.recommender import recommend

def test_ranking_order():
    items = [{"id": "c", "score": 5}, {"id": "a", "score": 5}, {"id": "b", "score": 5}]
    assert recommend(items) == ["a", "b", "c"]