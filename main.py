"""CLI wrapper for send_mail package.

Usage: run this module to send a simple email from the command line.
This is a lightweight helper; for programmatic use import `send_mail.send_email`.
"""
from __future__ import annotations

import argparse
from send_mail import send_email
from typing import List


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
    p.add_argument("--no-tls", action="store_true", help="Disable STARTTLS (only applies if not using SSL)")
    p.add_argument("--attach", action="append", help="Path to attachment (can be repeated)")
    return p.parse_args()


def _to_list(s: str) -> List[str]:
    return [part.strip() for part in s.split(",") if part.strip()]


def main() -> None:
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
