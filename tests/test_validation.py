import pytest
from src.validation import validate, ValidationError


def test_error_message():
    with pytest.raises(ValidationError) as exc_info:
        validate(None)
    assert str(exc_info.value) == 'Invalid value provided'