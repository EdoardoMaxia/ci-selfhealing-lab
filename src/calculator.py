def add(a, b):
    """Somma due numeri."""
    return a + b

def divide(a, b):
    """Divide a per b. Solleva errore se b è zero."""
    if b == 0:
        raise ValueError("Divisione per zero non permessa")
    return a / b

def factorial(n):
    """Calcola il fattoriale di n."""
    if n < 0:
        raise ValueError("n deve essere >= 0")
    if n == 0:
        return 1
    return n * factorial(n - 1)