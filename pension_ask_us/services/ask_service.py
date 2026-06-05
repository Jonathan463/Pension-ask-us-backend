"""Use-case service for answering a question against the knowledge base."""
from __future__ import annotations

from typing import List, Optional

from ..exceptions import EmptyKnowledgeBaseError, InvalidQuestionError
from ..generation.generator import AnswerGenerator
from ..retrieval.service import RetrievalService
from ..schemas import AskResponse, RetrievedChunk, Source
from ..vector_store.store import VectorStore


class AskService:
    """Coordinates retrieval, generation, and source formatting for /ask.

    The service depends only on abstractions and signals failures by raising
    domain exceptions from :mod:`pension_ask_us.exceptions`; transport layers
    translate those into the appropriate response.
    """

    def __init__(
        self,
        retrieval: RetrievalService,
        generator: AnswerGenerator,
        vector_store: VectorStore,
    ) -> None:
        self._retrieval = retrieval
        self._generator = generator
        self._vector_store = vector_store

    def ask(self, question: str, top_k: Optional[int] = None) -> AskResponse:
        cleaned = (question or "").strip()
        if not cleaned:
            raise InvalidQuestionError("Question must not be empty.")

        if self._vector_store.count() == 0:
            raise EmptyKnowledgeBaseError(
                "Knowledge base is empty. Run ingestion before asking."
            )

        retrieved = self._retrieval.retrieve(cleaned, top_k=top_k)
        answer = self._generator.generate(cleaned, retrieved)
        sources = self._build_sources(retrieved)
        top_source = self._pick_top_source(sources)
        return AskResponse(
            question=cleaned,
            answer=answer,
            sources=sources,
            top_source=top_source,
        )

    @staticmethod
    def _build_sources(retrieved: List[RetrievedChunk]) -> List[Source]:
        """Collapse retrieved chunks to one Source per URL, keeping best score."""
        unique: dict[str, Source] = {}
        for rc in retrieved:
            candidate = Source(title=rc.chunk.title, url=rc.chunk.url, score=rc.score)
            existing = unique.get(candidate.url)
            if existing is None or candidate.score > existing.score:
                unique[candidate.url] = candidate
        return list(unique.values())

    @staticmethod
    def _pick_top_source(sources: List[Source]) -> Optional[Source]:
        """Return the single highest-scoring deduplicated source, if any."""
        if not sources:
            return None
        return max(sources, key=lambda s: s.score)
