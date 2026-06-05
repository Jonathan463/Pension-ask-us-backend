"""Pydantic data models shared across modules."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Article(BaseModel):
    """A cleaned source article ready for chunking."""

    url: str
    title: str
    content: str


class Chunk(BaseModel):
    """A retrievable unit of text derived from an :class:`Article`."""

    id: str
    url: str
    title: str
    text: str
    position: int = 0


class RetrievedChunk(BaseModel):
    """A chunk returned by similarity search, with its score."""

    chunk: Chunk
    score: float


# ----- API payloads -----

class AskRequest(BaseModel):
    question: str = Field(..., min_length=2, description="Natural-language query")
    top_k: Optional[int] = Field(None, ge=1, le=20)


class Source(BaseModel):
    title: str
    url: str
    score: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[Source]
    top_source: Optional[Source] = None


class IngestRequest(BaseModel):
    urls: Optional[List[str]] = Field(
        default=None,
        description="Override the configured article URLs. Uses defaults when omitted.",
    )


class IngestResponse(BaseModel):
    articles_ingested: int
    chunks_indexed: int


class ShareRequest(BaseModel):
    recipient: str = Field(..., min_length=3, description="Recipient email address")
    question: str = Field(..., min_length=1)
    article_title: str = Field(..., min_length=1)
    article_url: str = Field(..., min_length=1)
    note: Optional[str] = Field(default=None, max_length=2000)


class ShareResponse(BaseModel):
    recipient: str
    article_url: str
