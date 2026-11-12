def add(a, b):
    """Adds two numbers."""
    return a + b

def divide(a, b):
    """Divides a by b. Raises an error if b is zero."""
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    return a / b

def factorial(n):
    """Computes the factorial of n."""
    if n < 0:
        raise ValueError("n must be >= 0")
    if n == 0:
        return 1
    return n * factorial(n - 1)

def power(base, exponent):
    """Raises base to exponent."""
    return base ** exponent