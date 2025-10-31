"""CLI wrapper for send_mail package.

Usage: run this module to send a simple email from the command line.
This is a lightweight helper; for programmatic use import `send_mail.send_email`.
"""
from __future__ import annotations

import argparse
from typing import List
from send_mail import send_email


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Send an email via custom SMTP server")
    p.add_argument("--smtp-server", required=True, help="SMTP server hostname or IP")
    p.add_argument("--smtp-port", type=int, default=587, help="SMTP server port")
    p.add_argument("--username", help="SMTP username (optional)")
    p.add_argument("--password", help="SMTP password (optional)")
    p.add_argument("--from", dest="sender", help="From email address")
    p.add_argument("--to", required=True, help="Recipient(s) (comma separated)")
    p.add_argument("--subject", default="", help="Email subject")
    p.add_argument("--body", default="", help="Email body")
    p.add_argument("--html", action="store_true", help="Send body as HTML")
    p.add_argument("--use-ssl", action="store_true", help="Use SMTPS (SSL) instead of STARTTLS")
    p.add_argument("--no-tls", action="store_true", help="Disable STARTTLS")
    p.add_argument("--attach", action="append", help="Path to attachment (can be repeated)")
    return p.parse_args()


def _to_list(s: str) -> List[str]:
    return [part.strip() for part in s.split(",") if part.strip()]


def main() -> None:
    """
    Parse command-line arguments and send an email based on those arguments.

    This function is the program entry point for a small CLI email sender. It:
    - Parses command-line arguments via _parse_args().
    - Builds a call to send_email(...) using parsed values:
        smtp_server, smtp_port, sender, recipients (converted from args.to),
        subject, body, html flag, username, password, use_ssl, use_tls, and attachments.
    - Converts an empty attachments list to None before passing to send_email.
    - Uses the inverse of args.no_tls to determine whether to enable STARTTLS.

    Side effects:
    - Establishes an SMTP connection and attempts to send an email.
    - May read files referenced by attachment paths.

    Returns:
    - None

    Raises:
    - Any exceptions raised by _parse_args() for invalid arguments.
    - Any exceptions propagated from send_email(), 
        such as SMTP/connection errors or file I/O errors 
        when reading attachments.

    Notes:
    - This function assumes helper functions 
        _parse_args(), 
        _to_list(), 
        and send_email(...) 
        are defined elsewhere in the module.
    """
    args = _parse_args()
    send_email(
        smtp_server=args.smtp_server,
        smtp_port=args.smtp_port,
        sender=args.sender,
        recipients=_to_list(args.to),
        subject=args.subject,
        body=args.body,
        html=args.html,
        username=args.username,
        password=args.password,
        use_ssl=args.use_ssl,
        use_tls=not args.no_tls,
        attachments=args.attach or None,
    )


if __name__ == "__main__":
    main()
