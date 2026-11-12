"""
Isolated unit test for strip_think_blocks() — does NOT call any LLM API.

router.py imports the various SDKs (langchain_anthropic, langchain_groq, ...) only
inside get_llm(), so simply importing the module to use
strip_think_blocks() does not make any network call.
"""
import pytest

from agent.agents.router import strip_think_blocks


def test_no_think_block_passthrough():
    text = '{"action": "fix", "file": "requirements.txt"}'
    assert strip_think_blocks(text) == text


def test_think_block_followed_by_json():
    text = '<think>reasoning about what to do</think>{"action": "fix"}'
    assert strip_think_blocks(text) == '{"action": "fix"}'


def test_multiline_think_block_followed_by_json():
    text = (
        "<think>\n"
        "first reasoning step\n"
        "second reasoning step\n"
        "</think>\n"
        '{"action": "fix", "file": "config.yml"}'
    )
    assert strip_think_blocks(text) == '{"action": "fix", "file": "config.yml"}'


def test_only_think_block_no_json_returns_empty_string():
    text = "<think>only reasoning, no final answer</think>"
    assert strip_think_blocks(text) == ""


def test_text_before_think_block_and_json_after():
    text = (
        "Here is my analysis:\n"
        "<think>evaluating the possible options</think>\n"
        '{"action": "fix", "file": "test_calculator.py"}'
    )
    result = strip_think_blocks(text)
    assert "<think>" not in result
    assert "</think>" not in result
    assert result.endswith('{"action": "fix", "file": "test_calculator.py"}')
