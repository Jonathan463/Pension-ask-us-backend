"""Email-delivery adapters used by the share endpoint."""
from .sender import EmailMessage, EmailSender
from .smtp import SmtpEmailSender

__all__ = [
    "EmailMessage",
    "EmailSender",
    "SmtpEmailSender",
]
