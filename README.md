# send_mail

Small utility package that provides a single function to send email via a configurable SMTP server.

Features:
- Use custom SMTP host and port
- Optional STARTTLS or SSL
- Optional authentication
- Attachments supported

Usage (programmatic):

from send_mail import send_email

send_email(
    smtp_server="smtp.example.com",
    smtp_port=587,
    username="user",
    password="pass",
    sender="me@example.com",
    recipients=["you@example.com"],
    subject="Hello",
    body="This is a test",
)

CLI usage:
python main.py --smtp-server smtp.example.com --to you@example.com --subject hi --body "hello"
