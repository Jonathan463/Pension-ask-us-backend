"""Split cleaned articles into overlapping retrieval chunks."""
from __future__ import annotations

import hashlib
import re
from typing import List

from ..schemas import Article, Chunk


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")


class TextChunker:
    """Sentence-aware sliding window chunker."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be in [0, chunk_size)")
        self._chunk_size = chunk_size
        self._overlap = chunk_overlap

    def chunk(self, article: Article) -> List[Chunk]:
        sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(article.content) if s.strip()]
        if not sentences:
            return []

        chunks: List[str] = []
        buffer: List[str] = []
        buffer_len = 0
        for sentence in sentences:
            sentence_len = len(sentence) + 1
            if buffer_len + sentence_len > self._chunk_size and buffer:
                chunks.append(" ".join(buffer))
                buffer, buffer_len = self._carry_over(buffer)
            buffer.append(sentence)
            buffer_len += sentence_len
        if buffer:
            chunks.append(" ".join(buffer))

        return [
            Chunk(
                id=self._chunk_id(article.url, idx, text),
                url=article.url,
                title=article.title,
                text=text,
                position=idx,
            )
            for idx, text in enumerate(chunks)
        ]

    # ---- helpers ----

    def _carry_over(self, buffer: List[str]) -> tuple[List[str], int]:
        """Keep trailing sentences as overlap for the next chunk."""
        carry: List[str] = []
        carry_len = 0
        for sentence in reversed(buffer):
            if carry_len + len(sentence) + 1 > self._overlap:
                break
            carry.insert(0, sentence)
            carry_len += len(sentence) + 1
        return carry, carry_len

    @staticmethod
    def _chunk_id(url: str, position: int, text: str) -> str:
        digest = hashlib.sha1(f"{url}|{position}|{text}".encode("utf-8")).hexdigest()
        return digest[:16]
