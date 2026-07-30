class ValidatorConfig:
    REQUIRE_TLD = True


def validate_email(value):
    """Validazione email minimale (per test_015)."""
    if "@" not in value:
        return False
    domain = value.split("@", 1)[1]
    if ValidatorConfig.REQUIRE_TLD and "." not in domain:
        return False
    return True
