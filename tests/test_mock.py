from unittest.mock import MagicMock, patch
from src.mailer import notify_user


def test_email_send():
    mock_smtp = MagicMock()
    notify_user(mock_smtp, "user@example.com", "subject", "body")
    mock_smtp.send_email.assert_called_once_with("user@example.com", "subject", "body")


def test_email_send_multiple_recipients():
    mock_smtp = MagicMock()
    notify_user(mock_smtp, "user1@example.com", "test", "message")
    notify_user(mock_smtp, "user2@example.com", "test", "message")
    assert mock_smtp.send_email.call_count == 2


def test_email_send_with_empty_body():
    mock_smtp = MagicMock()
    notify_user(mock_smtp, "user@example.com", "subject", "")
    mock_smtp.send_email.assert_called_once_with("user@example.com", "subject", "")


def test_email_send_called_with_correct_args():
    mock_smtp = MagicMock()
    email = "test@example.com"
    subject = "Test Subject"
    body = "Test Body"
    notify_user(mock_smtp, email, subject, body)
    mock_smtp.send_email.assert_called_once_with(email, subject, body)