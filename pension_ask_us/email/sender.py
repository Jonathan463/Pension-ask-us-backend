"""Email-sender abstraction."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


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
    def send(self, message: EmailMessage) -> None:
        """Deliver ``message`` or raise :class:`EmailDeliveryError`."""
