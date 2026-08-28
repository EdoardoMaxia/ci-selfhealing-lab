from src.summary import render_summary

def test_render_summary():
    result = render_summary(1234.56)
    assert str(result) == "Total: $1,234.56"