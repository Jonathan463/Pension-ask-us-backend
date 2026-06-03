"""HTTP fetching of raw article HTML."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import httpx

from ..exceptions import ArticleFetchError

logger = logging.getLogger(__name__)


class ArticleFetcher(ABC):
    """Fetches the raw HTML for a given URL."""

    @abstractmethod
    def fetch(self, url: str) -> str:
        """Return the raw HTML, or raise :class:`ArticleFetchError`."""


class HttpArticleFetcher(ArticleFetcher):
    """Synchronous HTTP fetcher built on httpx."""

    def __init__(
        self,
        timeout_seconds: float = 20.0,
        user_agent: str = "PensionAskUs/0.1",
    ) -> None:
        self._client = httpx.Client(
            timeout=timeout_seconds,
            headers={"User-Agent": user_agent},
            follow_redirects=True,
        )

    def fetch(self, url: str) -> str:
        try:
            response = self._client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ArticleFetchError(
                f"Failed to fetch article from {url}",
                details={"url": url, "cause": str(exc)},
            ) from exc
        return response.text

    def close(self) -> None:
        self._client.close()

    def __del__(self) -> None:  # best-effort cleanup
        try:
            self.close()
        except Exception:
            pass
