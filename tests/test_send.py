"""Unit tests for send_mail.smtp_sender module."""

import unittest
from unittest.mock import patch

import send_mail.smtp_sender as sender_mod


class FakeSMTP:
    """Fake SMTP connection object for tests."""
    def __init__(self, host, port, timeout=None):
        """Create a fake SMTP connection object for tests.

        Records connection parameters and provides no-op or stateful
        implementations of methods used by the sender (ehlo, starttls,
        login, send_message, quit, close). Tests inspect the attributes
        to assert expected behavior (e.g. that starttls was called).

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
        SMTP object's method signature so the sender can call it safely.
        """
        return

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
        # basic sanity checks on message
        """Validate the message has basic headers and mark it sent.

        Performs simple assertions to ensure the sender populated
        From/To headers, then records that send_message was called
        by setting ``sent`` to True.
        """
        assert msg["From"]
        assert msg["To"]
        self.sent = True

    def quit(self):
        """Simulate closing the SMTP session politely (QUIT).

        No-op for the fake; present so the sender's cleanup code can call it.
        """
        return

    def close(self):
        """Force-close the underlying connection.

        No-op for the fake; provided to mirror smtplib.SMTP's API.
        """
        return


class FakeSMTPSSL(FakeSMTP):
    """Fake SMTP_SSL connection object for tests."""


class SendEmailTests(unittest.TestCase):
    """Unit test to effectively test send_email function behavior."""
    @patch("smtplib.SMTP", autospec=True)
    def test_send_with_starttls_and_auth(self, mock_smtp_class):
        """Verify STARTTLS is used, authentication occurs, and a message is sent.

        This test patches smtplib.SMTP to return a FakeSMTP instance. It then
        calls send_email with use_tls=True and credentials and asserts that
        starttls, login and send_message were invoked on the fake object.
        """
        fake = FakeSMTP("smtp.example", 587, timeout=10)
        mock_smtp_class.return_value = fake

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

        # assert starttls happened and login and send
        self.assertTrue(fake.started_tls)
        self.assertTrue(fake.logged_in)
        self.assertTrue(fake.sent)

    @patch("smtplib.SMTP_SSL", autospec=True)
    def test_send_with_ssl_no_auth(self, mock_ssl_class):
        """Verify SSL connection path sends message without STARTTLS.

        This test patches smtplib.SMTP_SSL to return a FakeSMTPSSL instance
        and verifies that the SSL code path sends the message and does not
        call starttls (SSL does not require STARTTLS).
        """
        fake = FakeSMTPSSL("smtp.example", 465, timeout=10)
        mock_ssl_class.return_value = fake

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

        # ssl path should not call starttls, but should send
        self.assertFalse(fake.started_tls)
        self.assertTrue(fake.sent)


if __name__ == "__main__":
    unittest.main()
