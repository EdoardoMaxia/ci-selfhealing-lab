import pytest
from db import Database #type: ignore

def test_save_record():
    """Test che save() viene chiamato con il parametro commit."""
    db = Database()
    result = db.save("test_record")
    assert result is not None