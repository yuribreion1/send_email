"""send_mail package

Public API:
- send_email: send an email via a configurable SMTP server
"""

from .smtp_sender import send_email

__all__ = ["send_email"]
