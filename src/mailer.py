def notify_user(smtp, to, subject, body):
    """Invia una notifica email tramite il client smtp fornito (per test_013)."""
    smtp.send_email(to, subject, body)
