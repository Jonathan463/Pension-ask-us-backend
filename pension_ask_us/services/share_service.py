"""Use-case service for sharing the top-ranked article by email."""
from __future__ import annotations

import re

from ..email import EmailMessage, EmailSender
from ..exceptions import InvalidEmailError
from ..schemas import ShareRequest, ShareResponse

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ShareService:
    """Format the share email and hand it to the configured EmailSender."""

    def __init__(
        self,
        *,
        sender: EmailSender,
        from_address: str,
    ) -> None:
        self._sender = sender
        self._from = from_address

    def share(self, payload: ShareRequest) -> ShareResponse:
        recipient = (payload.recipient or "").strip()
        if not _EMAIL_RE.match(recipient):
            raise InvalidEmailError(
                "Recipient email address is not valid.",
                details={"recipient": payload.recipient},
            )

        subject = f"NHS pension info: {payload.article_title}"
        body = self._render_body(payload)
        self._sender.send(
            EmailMessage(
                sender=self._from,
                recipient=recipient,
                subject=subject,
                body=body,
            )
        )
        return ShareResponse(
            recipient=recipient,
            article_url=payload.article_url,
        )

    @staticmethod
    def _render_body(payload: ShareRequest) -> str:
        lines = [
            "Hello,",
            "",
            "Someone used Pension Ask Us to look up an answer to:",
            f"  {payload.question}",
            "",
            "The most relevant NHS Pensions article is:",
            f"  {payload.article_title}",
            f"  {payload.article_url}",
        ]
        if payload.note:
            lines += ["", "Note from the sender:", payload.note]
        lines += ["", "-- Pension Ask Us"]
        return "\n".join(lines)
