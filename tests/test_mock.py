from unittest.mock import MagicMock
from src.mailer import notify_user


def test_email_send():
    mock_smtp = MagicMock()
    notify_user(mock_smtp, "user@example.com", "subject", "body")
    mock_smtp.send_email.assert_called_once_with("user@example.com", "subject", "body")


def test_email_send_with_different_recipient():
    mock_smtp = MagicMock()
    notify_user(mock_smtp, "another@example.com", "test subject", "test body")
    mock_smtp.send_email.assert_called_once_with("another@example.com", "test subject", "test body")


def test_email_send_called_once():
    mock_smtp = MagicMock()
    notify_user(mock_smtp, "user@example.com", "subject", "body")
    assert mock_smtp.send_email.call_count == 1


def test_email_send_multiple_calls():
    mock_smtp = MagicMock()
    notify_user(mock_smtp, "user1@example.com", "subject1", "body1")
    notify_user(mock_smtp, "user2@example.com", "subject2", "body2")
    assert mock_smtp.send_email.call_count == 2