from src.utils import to_upper

def test_string_upper():
    assert to_upper('hello') == 'HELLO'

def test_string_upper_correct():
    assert to_upper('hello') == 'hello'
```

Aggiungi il secondo test per verificare che la funzione `to_upper` restituisca la stringa in maiuscolo.

```python
def test_string_upper_correct():
    assert to_upper('hello') == 'HELLO'
```
