"""Extracts the meaningful article body from raw NHSBSA knowledge-base HTML."""
from __future__ import annotations

import re
from typing import Optional

from bs4 import BeautifulSoup

from ..schemas import Article


_STRIP_TAGS = ("script", "style", "noscript", "iframe", "svg", "form", "nav", "footer")

_PRIMARY_SELECTORS = (
    "div.knowledge-article-content",
    "div.knowledge-article",
    "article",
    "main",
)


class HtmlCleaner:
    """Turns a raw HTML string into a clean :class:`Article`."""

    def clean(self, url: str, html: str) -> Optional[Article]:
        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")

        for tag_name in _STRIP_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        title = self._extract_title(soup)
        body = self._extract_body(soup)
        text = self._normalise_whitespace(body)

        if len(text) < 40:
            return None

        return Article(url=url, title=title or url, content=text)

    def _extract_title(self, soup: BeautifulSoup) -> str:
        for selector in ("h1", "title"):
            tag = soup.select_one(selector)
            if tag and tag.get_text(strip=True):
                return tag.get_text(strip=True)
        return ""

    def _extract_body(self, soup: BeautifulSoup) -> str:
        for selector in _PRIMARY_SELECTORS:
            node = soup.select_one(selector)
            if node:
                text = node.get_text(separator="\n", strip=True)
                if len(text) > 80:
                    return text
        body = soup.body or soup
        return body.get_text(separator="\n", strip=True)

    def _normalise_whitespace(self, text: str) -> str:
        lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
        lines = [ln for ln in lines if ln]
        return "\n".join(lines)
