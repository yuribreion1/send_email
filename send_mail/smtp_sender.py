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
    if isinstance(recipients, (list, tuple)):
        return list(recipients)
    return [r.strip() for r in str(recipients).split(",") if r.strip()]


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
    """Send an email.

    Args:
        smtp_server: hostname or IP of SMTP server.
        smtp_port: port to connect to (defaults: 587 for STARTTLS, 465 for SSL).
        sender: envelope From address. If None and username provided, username is used.
        recipients: single address or list/comma-separated string of recipients.
        subject: message subject.
        body: message body (plain text or HTML depending on `html`).
        html: whether body should be sent as HTML.
        username: username for authentication (optional).
        password: password for authentication (optional).
        use_tls: whether to use STARTTLS (only when use_ssl is False).
        use_ssl: whether to use SMTPS (connect with SSL). If True, `use_tls` is ignored.
        attachments: list of file paths to attach.
        timeout: socket timeout in seconds.

    Raises:
        FileNotFoundError: if an attachment path doesn't exist.
        smtplib.SMTPException: if sending fails.
    """

    if recipients is None:
        raise ValueError("recipients must be provided")

    to_addrs = _ensure_list(recipients)
    if not to_addrs:
        raise ValueError("no recipients parsed from recipients argument")

    if sender is None:
        sender = username or "noreply@example.com"

    msg = EmailMessage()
    msg["From"] = sender
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
            ctype, encoding = mimetypes.guess_type(path)
            if ctype is None:
                ctype = "application/octet-stream"
            maintype, subtype = ctype.split("/", 1)
            with open(path, "rb") as fp:
                data = fp.read()
            msg.add_attachment(
                data, 
                maintype=maintype, 
                subtype=subtype, 
                filename=os.path.basename(path))

    # Establish connection and send
    if use_ssl:
        smtp_class = smtplib.SMTP_SSL
    else:
        smtp_class = smtplib.SMTP

    server = smtp_class(smtp_server, smtp_port, timeout=timeout)
    try:
        if not use_ssl and use_tls:
            server.ehlo()
            server.starttls()
            server.ehlo()

        if username:
            server.login(username, password or "")

        server.send_message(msg)
    finally:
        try:
            server.quit()
        except Exception:
            # best-effort close
            try:
                server.close()
            except Exception:
                pass
