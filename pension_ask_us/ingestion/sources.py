"""Sources that yield article URLs to ingest."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List


class ArticleSource(ABC):
    """Provides URLs of articles to be ingested."""

    @abstractmethod
    def urls(self) -> List[str]:
        """Return the list of URLs to ingest."""


class StaticUrlSource(ArticleSource):
    """An article source backed by a fixed list of URLs."""

    def __init__(self, urls: Iterable[str]) -> None:
        self._urls: List[str] = [u for u in urls if u]

    def urls(self) -> List[str]:
        return list(self._urls)
