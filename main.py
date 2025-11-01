"""CLI wrapper for send_mail package.

Usage: for programmatic use import `send_mail.EmailSender`.
"""
from __future__ import annotations

import argparse
from typing import List
from send_mail import EmailSender


def _parse_args() -> argparse.Namespace:
    """Build and parse the command-line arguments for the CLI.

    Returns an argparse.Namespace with the parsed CLI options. This helper
    centralizes the flag definitions used by the module-level CLI `main()`.

    Flags include SMTP connection options, credentials, from/to/subject/body,
    HTML flag, and attachments.
    """
    parser = argparse.ArgumentParser(description="Send an email via custom SMTP server")
    parser.add_argument(
        "--smtp-server", required=True, help="SMTP server hostname or IP"
    )
    parser.add_argument("--smtp-port", type=int, default=587, help="SMTP server port")
    parser.add_argument("--username", help="SMTP username (optional)")
    parser.add_argument("--password", help="SMTP password (optional)")
    parser.add_argument("--from", dest="sender", help="From email address")
    parser.add_argument("--to", required=True, help="Recipient(s) (comma separated)")
    parser.add_argument("--subject", default="", help="Email subject")
    parser.add_argument("--body", default="", help="Email body")
    parser.add_argument("--html", action="store_true", help="Send body as HTML")
    parser.add_argument(
        "--use-ssl", action="store_true", help="Use SMTPS (SSL) instead of STARTTLS"
    )
    parser.add_argument("--no-tls", action="store_true", help="Disable STARTTLS")
    parser.add_argument(
        "--attach", action="append", help="Path to attachment (can be repeated)"
    )
    return parser.parse_args()


def _to_list(s: str) -> List[str]:
    """Convert a comma-separated string into a list of stripped values.

    Example: "a@example.com, b@example.com" -> ["a@example.com", "b@example.com"]

    Args:
        s: A comma-separated string.

    Returns:
        List[str]: The non-empty, stripped components of the input string.
    """
    return [part.strip() for part in s.split(",") if part.strip()]


def main() -> None:
    """
    Parse command-line arguments and send an email based on those arguments.

    This function is the program entry point for a small CLI email sender. It:
    - Parses command-line arguments via _parse_args().
    - Creates an EmailSender instance with SMTP connection settings.
    - Uses the inverse of args.no_tls to determine whether to enable STARTTLS.

    Side effects:
    - Establishes an SMTP connection and attempts to send an email.
    - May read files referenced by attachment paths.

    Returns:
    - None
    """
    args = _parse_args()
    # Create sender with connection settings
    sender = EmailSender(
        smtp_server=args.smtp_server,
        smtp_port=args.smtp_port,
        username=args.username,
        password=args.password,
        use_ssl=args.use_ssl,
        use_tls=not args.no_tls,
        sender=args.sender,
    )
    # Send the message
    sender.send(
        recipients=_to_list(args.to),
        subject=args.subject,
        body=args.body,
        html=args.html,
    )


if __name__ == "__main__":
    main()
