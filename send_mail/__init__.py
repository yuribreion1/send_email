"""send_mail package

Public API:
- EmailSender: class for sending emails via configurable SMTP server
- send_email: legacy function API for sending emails (prefer EmailSender)
"""

from .smtp_sender import EmailSender, send_email

__all__ = ["EmailSender", "send_email"]
