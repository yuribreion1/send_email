"""SMTP email sender utility.

Provides a single function `send_email` that sends an email using a configurable
SMTP server (host/port), optional TLS/SSL and authentication. Uses stdlib only
so it can be packaged for Anaconda without extra dependencies.
"""
from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import List, Optional, Union
import mimetypes
import os


def _ensure_list(recipients: Union[str, List[str]]) -> List[str]:
    """Normalize recipients into a list of address strings.

    Accepts either a list/tuple of addresses or a comma-separated string and
    returns a list of stripped, non-empty recipient strings.

    Examples:
        _ensure_list("a@example.com,b@example.com") -> ["a@example.com", "b@example.com"]
        _ensure_list(["a@example.com"]) -> ["a@example.com"]

    Args:
        recipients: A single comma-separated string or an iterable of strings.

    Returns:
        List[str]: A list of recipient email addresses.
    """
    if isinstance(recipients, (list, tuple)):
        return list(recipients)
    return [r.strip() for r in str(recipients).split(",") if r.strip()]


class EmailSender:
    """Email sender that connects to a specified SMTP server.

    This class provides email sending functionality with optional STARTTLS/SSL,
    authentication, and file attachments. Uses Python's standard library only.

    Example:
        sender = EmailSender("smtp.example.com", username="user", password="pass")
        sender.send(recipients="you@example.com", subject="Hi", body="Test")
    """

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
        use_ssl: bool = False,
        sender: str | None = None,
        timeout: Optional[float] = 10.0,
    ) -> None:
        """Initialize EmailSender with SMTP connection settings.

        Args:
            smtp_server: hostname or IP of SMTP server.
            smtp_port: port to connect to (defaults: 587 for STARTTLS, 465 for SSL).
            username: username for authentication.
            password: password for authentication.
            use_tls: whether to use STARTTLS (only when use_ssl is False).
            use_ssl: whether to use SMTPS (connect with SSL). If True, `use_tls` is ignored.
            sender: envelope From address. If None and username provided, username is used.
            timeout: socket timeout in seconds.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.sender = sender or username or "noreply@example.com"
        self.timeout = timeout

    def send(
        self,
        recipients: Union[str, List[str]] | None = None,
        subject: str = "",
        body: str = "",
        html: bool = False,
        attachments: Optional[List[str]] = None,
    ) -> None:
        """Send an email using the configured SMTP settings.

        Args:
            recipients: single address or list/comma-separated string of recipients.
            subject: message subject.
            body: message body (plain text or HTML depending on `html`).
            html: whether body should be sent as HTML.
            attachments: list of file paths to attach.

        Raises:
            ValueError: if recipients is None or empty.
            FileNotFoundError: if an attachment path doesn't exist.
            smtplib.SMTPException: if sending fails.
        """
        if recipients is None:
            raise ValueError("recipients must be provided")

        to_addrs = _ensure_list(recipients)
        if not to_addrs:
            raise ValueError("no recipients parsed from recipients argument")

        msg = EmailMessage()
        msg["From"] = self.sender
        msg["To"] = ", ".join(to_addrs)
        msg["Subject"] = subject

        if html:
            msg.add_alternative(body, subtype="html")
        else:
            msg.set_content(body)

        # Attach files if provided
        if attachments:
            for path in attachments:
                if not os.path.isfile(path):
                    raise FileNotFoundError(f"attachment not found: {path}")
                ctype, _ = mimetypes.guess_type(path)
                if ctype is None:
                    ctype = "application/octet-stream"
                maintype, subtype = ctype.split("/", 1)
                with open(path, "rb") as fp:
                    data = fp.read()
                msg.add_attachment(
                    data,
                    maintype=maintype,
                    subtype=subtype,
                    filename=os.path.basename(path),
                )

        # Establish connection and send
        if self.use_ssl:
            smtp_class = smtplib.SMTP_SSL
        else:
            smtp_class = smtplib.SMTP

        server = smtp_class(self.smtp_server, self.smtp_port, timeout=self.timeout)
        try:
            if not self.use_ssl and self.use_tls:
                server.ehlo()
                server.starttls()
                server.ehlo()

            if self.username:
                server.login(self.username, self.password or "")

            server.send_message(msg)
        finally:
            try:
                server.quit()
            except smtplib.SMTPResponseException:
                try:
                    server.close()
                except smtplib.SMTPResponseException:
                    pass


# Legacy function API for backward compatibility
def send_email(
    smtp_server: str,
    smtp_port: int = 587,
    sender: str | None = None,
    recipients: Union[str, List[str]] | None = None,
    subject: str = "",
    body: str = "",
    html: bool = False,
    username: Optional[str] = None,
    password: Optional[str] = None,
    use_tls: bool = True,
    use_ssl: bool = False,
    attachments: Optional[List[str]] = None,
    timeout: Optional[float] = 10.0,
) -> None:
    """Send an email (legacy function API, prefer using EmailSender class).

    This function provides backward compatibility with the old API.
    New code should use the EmailSender class instead.

    Args:
        smtp_server: hostname or IP of SMTP server.
        smtp_port: port to connect to (587 for STARTTLS, 465 for SSL).
        sender: envelope From address.
        recipients: list/comma-separated string of recipients.
        subject: message subject.
        body: message body (plain text or HTML depending on `html`).
        html: whether body should be sent as HTML.
        username: username for authentication.
        password: password for authentication.
        use_tls: whether to use STARTTLS
        use_ssl: whether to use SMTPS. If True, `use_tls` is ignored.
        attachments: list of file paths to attach.
        timeout: socket timeout in seconds.

    Raises:
        FileNotFoundError: if an attachment path doesn't exist.
        smtplib.SMTPException: if sending fails.
    """
    sender = EmailSender(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        username=username,
        password=password,
        use_tls=use_tls,
        use_ssl=use_ssl,
        sender=sender,
        timeout=timeout,
    )
    sender.send(
        recipients=recipients,
        subject=subject,
        body=body,
        html=html,
        attachments=attachments,
    )
