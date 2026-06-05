"""Email-delivery adapters used by the share endpoint."""
from .sender import ConsoleEmailSender, EmailMessage, EmailSender
from .smtp import SmtpEmailSender

__all__ = [
    "ConsoleEmailSender",
    "EmailMessage",
    "EmailSender",
    "SmtpEmailSender",
]
