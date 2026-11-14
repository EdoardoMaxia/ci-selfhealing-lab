def notify_user(smtp, to, subject, body):
    """Sends an email notification through the provided smtp client (for test_013)."""
    smtp.send_email(to, subject, body)
