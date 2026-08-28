from unittest.mock import MagicMock
from src.mailer import notify_user


def test_email_send():
    mock_smtp = MagicMock()
    notify_user(mock_smtp, "user@example.com", "subject", "body")
    mock_smtp.send_message.assert_called_once()