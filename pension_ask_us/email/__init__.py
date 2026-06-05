"""Email-delivery adapters used by the share endpoint."""
from .sender import ConsoleEmailSender, EmailMessage, EmailSender

__all__ = ["ConsoleEmailSender", "EmailMessage", "EmailSender"]
