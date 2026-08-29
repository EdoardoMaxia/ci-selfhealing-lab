from src.summary import render_summary

def test_render_summary():
    result = render_summary(1234.56)
    assert result == "Total: $1,234.56"

def test_render_summary_with_dollar_symbol():
    result = render_summary(1234.56)
    assert result == "Total: $1,234.56"

def test_render_summary_with_decimal_places():
    result = render_summary(1234.56)
    assert result == "Total: $1,234.56"