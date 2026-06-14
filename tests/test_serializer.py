def test_json_serialize():
    """Test JSON serialization of date objects."""
    from datetime import date, datetime
    test_date = date(2024, 1, 15)
    result = test_date.strftime('%Y-%m-%d')
    assert result == '2024-01-15'