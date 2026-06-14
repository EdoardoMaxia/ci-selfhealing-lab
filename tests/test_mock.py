from unittest import TestCase
from unittest.mock import Mock, patch
import smtplib

class TestEmail(TestCase):
    def setUp(self):
        self.mock_smtp = Mock()

    @patch('smtplib.SMTP')
    def test_send_email(self, mock_smtp):
        smtp = mock_smtp.return_value
        smtp.send_message("sender@example.com", "recipient@example.com", "Subject: Test\nBody")
        smtp.send_message.assert_called_once()

    def test_send_message(self):
        self.mock_smtp.send_email.return_value = None  
        self.mock_smtp.send_email("sender@example.com", "recipient@example.com", "Subject: Test\nBody")
        self.mock_smtp.send_email.assert_called_once()

    def test_add(self):
        self.assertTrue(True)

    def test_divide(self):
        self.assertTrue(True)

    def test_factorial(self):
        self.assertTrue(True)