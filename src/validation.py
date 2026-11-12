class ValidationError(Exception):
    pass


def validate(value):
    """Validates value, raises ValidationError with a stable message (for test_040)."""
    if not value:
        raise ValidationError('Invalid value')
    return value
