from src.db import Database


def test_save_record():
    db = Database()
    assert db.save({"id": 1}, commit=True) is True