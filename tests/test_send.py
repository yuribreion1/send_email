"""Tests for send_mail package.

Tests both the EmailSender class and legacy send_email function.
Uses mocked SMTP classes to avoid real network calls.
"""
import unittest
from unittest.mock import patch

import send_mail.smtp_sender as sender_mod


class FakeSMTP:
    """Mock SMTP connection for testing.

    Records connection parameters and provides no-op or stateful
    implementations of methods used by EmailSender. Tests inspect
    the attributes to assert expected behavior.
    """

    def __init__(self, host, port, timeout=None):
        """Create a fake SMTP connection object for tests.

        Args:
            host: SMTP server host passed to constructor.
            port: SMTP server port passed to constructor.
            timeout: Optional socket timeout value.
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started_tls = False
        self.logged_in = False
        self.sent = False

    def ehlo(self):
        """Simulate an EHLO/HELO SMTP command.

        This fake implementation is a no-op but mirrors the real
        SMTP object's method signature so EmailSender can call it safely.
        """

    def starttls(self):
        """Mark that STARTTLS was invoked on the connection.

        Tests can assert that ``started_tls`` is True to verify the
        STARTTLS code path executed.
        """
        self.started_tls = True

    def login(self, username, password):
        """Record the credentials used to login.

        The test verifies that login was called with the expected
        username/password by inspecting the ``logged_in`` attribute.
        """
        self.logged_in = (username, password)

    def send_message(self, msg):
        """Validate the message has basic headers and mark it sent.

        Performs simple assertions to ensure EmailSender populated
        From/To headers, then records that send_message was called
        by setting ``sent`` to True.
        """
        # basic sanity checks on message
        assert msg["From"]
        assert msg["To"]
        self.sent = True

    def quit(self):
        """Simulate closing the SMTP session politely (QUIT).

        No-op for the fake; present so EmailSender's cleanup code can call it.
        """

    def close(self):
        """Force-close the underlying connection.

        No-op for the fake; provided to mirror smtplib.SMTP's API.
        """


class FakeSMTPSSL(FakeSMTP):
    """Mock SMTP_SSL connection, inherits FakeSMTP behavior."""


class SendEmailTests(unittest.TestCase):
    """Test suite for EmailSender class and send_email function."""

    @patch("smtplib.SMTP", autospec=True)
    def test_send_with_starttls_and_auth(self, mock_smtp_class):
        """Test authenticated email sending with STARTTLS.
        Creates an EmailSender with STARTTLS and auth enabled,
        sends a message, and verifies that:
        1. STARTTLS was initiated
        2. Login was called with credentials
        3. Message was sent
        """
        fake = FakeSMTP("smtp.example", 587, timeout=10)
        mock_smtp_class.return_value = fake

        # Test the new class API
        sender = sender_mod.EmailSender(
            smtp_server="smtp.example",
            smtp_port=587,
            username="user",
            password="pass",
            sender="me@example.com",
            use_ssl=False,
            use_tls=True,
        )
        sender.send(
            recipients=["you@example.com"],
            subject="hi",
            body="hello",
        )

        # assert starttls happened and login and send
        self.assertTrue(fake.started_tls)
        self.assertTrue(fake.logged_in)
        self.assertTrue(fake.sent)

        # Test the legacy function API
        fake.started_tls = False
        fake.logged_in = False
        fake.sent = False

        sender_mod.send_email(
            smtp_server="smtp.example",
            smtp_port=587,
            username="user",
            password="pass",
            sender="me@example.com",
            recipients=["you@example.com"],
            subject="hi",
            body="hello",
            use_ssl=False,
            use_tls=True,
        )

        # Legacy function should behave the same
        self.assertTrue(fake.started_tls)
        self.assertTrue(fake.logged_in)
        self.assertTrue(fake.sent)

    @patch("smtplib.SMTP_SSL", autospec=True)
    def test_send_with_ssl_no_auth(self, mock_ssl_class):
        """Test unauthenticated email sending with SSL.
        Creates an EmailSender with SSL enabled but no auth,
        sends a message, and verifies that:
        1. STARTTLS was not used (SSL connection instead)
        2. Message was sent successfully
        """
        fake = FakeSMTPSSL("smtp.example", 465, timeout=10)
        mock_ssl_class.return_value = fake

        # Test the new class API
        sender = sender_mod.EmailSender(
            smtp_server="smtp.example",
            smtp_port=465,
            sender="me@example.com",
            use_ssl=True,
            username=None,
        )
        sender.send(
            recipients="you@example.com",
            subject="hi",
            body="hello",
        )

        # ssl path should not call starttls, but should send
        self.assertFalse(fake.started_tls)
        self.assertTrue(fake.sent)

        # Test the legacy function API
        fake.started_tls = False
        fake.sent = False

        sender_mod.send_email(
            smtp_server="smtp.example",
            smtp_port=465,
            sender="me@example.com",
            recipients="you@example.com",
            subject="hi",
            body="hello",
            use_ssl=True,
            username=None,
        )

        # Legacy function should behave the same
        self.assertFalse(fake.started_tls)
        self.assertTrue(fake.sent)


if __name__ == "__main__":
    unittest.main()
