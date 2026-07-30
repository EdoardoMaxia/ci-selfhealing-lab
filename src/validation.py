class ValidationError(Exception):
    pass


def validate(value):
    """Valida value, solleva ValidationError con messaggio stabile (per test_040)."""
    if not value:
        raise ValidationError('Invalid value')
    return value
