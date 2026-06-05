"""Email-sender abstraction with a console (log-only) implementation."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmailMessage:
    """A fully-formed message ready for delivery."""

    sender: str
    recipient: str
    subject: str
    body: str


class EmailSender(ABC):
    """Abstraction over the concrete email backend."""

    @abstractmethod
    def send(self, message: EmailMessage) -> None:  # pragma: no cover - interface
        """Deliver ``message`` or raise :class:`EmailDeliveryError`."""


class ConsoleEmailSender(EmailSender):
    """Log emails instead of sending them.

    Intended for local development and demos so the share endpoint is
    exercisable end-to-end without real SMTP credentials.
    """

    def send(self, message: EmailMessage) -> None:
        logger.info(
            "[email/console] from=%s to=%s subject=%r\n%s",
            message.sender,
            message.recipient,
            message.subject,
            message.body,
        )
