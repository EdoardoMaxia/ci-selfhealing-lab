"""
Test unitario isolato per strip_think_blocks() — NON invoca nessuna API LLM.

router.py importa i vari SDK (langchain_anthropic, langchain_groq, ...) solo
dentro get_llm(), quindi il semplice import del modulo per usare
strip_think_blocks() non fa alcuna chiamata di rete.
"""
import pytest

from agent.agents.router import strip_think_blocks


def test_no_think_block_passthrough():
    text = '{"action": "fix", "file": "requirements.txt"}'
    assert strip_think_blocks(text) == text


def test_think_block_followed_by_json():
    text = '<think>ragiono sul da farsi</think>{"action": "fix"}'
    assert strip_think_blocks(text) == '{"action": "fix"}'


def test_multiline_think_block_followed_by_json():
    text = (
        "<think>\n"
        "primo passo di ragionamento\n"
        "secondo passo di ragionamento\n"
        "</think>\n"
        '{"action": "fix", "file": "config.yml"}'
    )
    assert strip_think_blocks(text) == '{"action": "fix", "file": "config.yml"}'


def test_only_think_block_no_json_returns_empty_string():
    text = "<think>solo ragionamento, nessuna risposta finale</think>"
    assert strip_think_blocks(text) == ""


def test_text_before_think_block_and_json_after():
    text = (
        "Ecco la mia analisi:\n"
        "<think>valuto le opzioni possibili</think>\n"
        '{"action": "fix", "file": "test_calculator.py"}'
    )
    result = strip_think_blocks(text)
    assert "<think>" not in result
    assert "</think>" not in result
    assert result.endswith('{"action": "fix", "file": "test_calculator.py"}')
