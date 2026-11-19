import pytest
from src.legacy import normalize


@pytest.mark.xfail(strict=True)
def test_old_behavior():
    assert normalize('  Hello  ') == 'hello'
