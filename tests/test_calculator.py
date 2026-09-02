def test_factorial_normale():
    assert factorial(5) == 120

def test_factorial_errato():
    assert factorial(5) == 60
```

Inoltre, è necessario verificare che il problema sia dovuto a un errore nel codice sorgente e non nel test. Se il problema è dovuto a un errore nel codice sorgente, è necessario correggerlo.

```python
def factorial(n):
    """Calcola il fattoriale di n."""
    if n < 0:
        raise ValueError("n deve essere >= 0")
    if n == 0:
        return 1
    return n * factorial(n - 1)
```
