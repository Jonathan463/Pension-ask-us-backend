"""SMTP-backed email sender (STARTTLS by default)."""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage as MimeEmailMessage

from ..exceptions import EmailDeliveryError
from .sender import EmailMessage, EmailSender

logger = logging.getLogger(__name__)


class SmtpEmailSender(EmailSender):
    """Send email via a real SMTP server.

    Uses STARTTLS when ``use_tls`` is true (the Gmail-on-587 path); falls
    back to a plain SMTP connection otherwise (useful for local relays
    such as MailHog). Any failure is wrapped in
    :class:`EmailDeliveryError` so it surfaces as a 502 to the caller.
    """

    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        timeout_seconds: float = 15.0,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._use_tls = use_tls
        self._timeout = timeout_seconds

    def send(self, message: EmailMessage) -> None:
        mime = MimeEmailMessage()
        mime["From"] = message.sender
        mime["To"] = message.recipient
        mime["Subject"] = message.subject
        mime.set_content(message.body)

        try:
            with smtplib.SMTP(self._host, self._port, timeout=self._timeout) as smtp:
                smtp.ehlo()
                if self._use_tls:
                    smtp.starttls()
                    smtp.ehlo()
                smtp.login(self._username, self._password)
                smtp.send_message(mime)
        except (smtplib.SMTPException, OSError) as exc:
            logger.error("SMTP send failed: %s", exc)
            raise EmailDeliveryError(
                "Failed to send email via SMTP.",
                details={"host": self._host, "port": self._port},
            ) from exc
