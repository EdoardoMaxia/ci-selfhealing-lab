import pytest
from src.validation import validate, ValidationError


def test_error_message():
    with pytest.raises(ValidationError, match='Invalid value'):
        validate(None)