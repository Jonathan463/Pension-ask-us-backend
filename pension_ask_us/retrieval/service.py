"""Coordinates embedding the query and searching the vector store."""
from __future__ import annotations

from typing import List

from ..embeddings.embedder import Embedder
from ..schemas import RetrievedChunk
from ..vector_store.store import VectorStore


class RetrievalService:
    """Single-responsibility orchestrator for similarity retrieval."""

    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        default_top_k: int = 4,
    ) -> None:
        if default_top_k <= 0:
            raise ValueError("default_top_k must be positive")
        self._embedder = embedder
        self._vector_store = vector_store
        self._default_top_k = default_top_k

    def retrieve(self, question: str, top_k: int | None = None) -> List[RetrievedChunk]:
        question = (question or "").strip()
        if not question:
            return []
        k = top_k or self._default_top_k
        vector = self._embedder.embed_one(question)
        return self._vector_store.query(vector, top_k=k)
