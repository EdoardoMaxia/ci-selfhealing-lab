from unittest.mock import patch
import app.notify


@patch('app.notify.send_email')
def test_send_alert(mock_send):
    app.notify.send_email("a@b.com", "subj", "body")
    mock_send.assert_called_once()
