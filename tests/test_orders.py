import pytest
from src.orders import create_order


@pytest.fixture
def db_session():
    return {}


def test_create_order(db_session):
    order = create_order(db_session, item_id=1)
    assert order["item_id"] == 1


def test_order_status(db_session):
    order = create_order(db_session, item_id=2)
    assert order["status"] == "new"