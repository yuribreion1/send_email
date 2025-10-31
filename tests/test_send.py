import unittest
from unittest.mock import patch

import send_mail.smtp_sender as sender_mod


class FakeSMTP:
    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started_tls = False
        self.logged_in = False
        self.sent = False

    def ehlo(self):
        return

    def starttls(self):
        self.started_tls = True

    def login(self, username, password):
        self.logged_in = (username, password)

    def send_message(self, msg):
        # basic sanity checks on message
        assert msg["From"]
        assert msg["To"]
        self.sent = True

    def quit(self):
        return

    def close(self):
        return


class FakeSMTPSSL(FakeSMTP):
    pass


class SendEmailTests(unittest.TestCase):
    @patch("smtplib.SMTP", autospec=True)
    def test_send_with_starttls_and_auth(self, mock_smtp_class):
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
