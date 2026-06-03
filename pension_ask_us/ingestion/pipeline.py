"""Orchestrates the ingestion pipeline: sources -> fetch -> clean -> chunk -> index."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

from ..embeddings.embedder import Embedder
from ..exceptions import ArticleFetchError
from ..schemas import Chunk
from ..vector_store.store import VectorStore
from .chunker import TextChunker
from .cleaner import HtmlCleaner
from .fetcher import ArticleFetcher
from .sources import ArticleSource

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    articles_ingested: int
    chunks_indexed: int


class IngestionPipeline:
    """Runs the article -> embedding -> vector store flow.

    Each collaborator is injected, so any step can be swapped without changing
    the orchestration logic (Open/Closed + Dependency Inversion).
    """

    def __init__(
        self,
        source: ArticleSource,
        fetcher: ArticleFetcher,
        cleaner: HtmlCleaner,
        chunker: TextChunker,
        embedder: Embedder,
        vector_store: VectorStore,
    ) -> None:
        self._source = source
        self._fetcher = fetcher
        self._cleaner = cleaner
        self._chunker = chunker
        self._embedder = embedder
        self._vector_store = vector_store

    def run(self, *, reset: bool = True) -> IngestionResult:
        if reset:
            self._vector_store.reset()

        urls = self._source.urls()
        logger.info("Ingesting %d URLs", len(urls))

        articles_ingested = 0
        all_chunks: List[Chunk] = []

        for url in urls:
            try:
                html = self._fetcher.fetch(url)
            except ArticleFetchError as exc:
                # Per-URL failures are recoverable: log and continue so a
                # single bad URL doesn't abort the whole run.
                logger.warning("Skipping %s: %s", url, exc.message)
                continue
            if not html:
                continue
            article = self._cleaner.clean(url, html)
            if not article:
                logger.info("Skipped (no usable content): %s", url)
                continue
            chunks = self._chunker.chunk(article)
            if not chunks:
                continue
            articles_ingested += 1
            all_chunks.extend(chunks)
            logger.info("Prepared %d chunks from %s", len(chunks), article.title)

        if not all_chunks:
            return IngestionResult(articles_ingested=0, chunks_indexed=0)

        vectors = self._embedder.embed([c.text for c in all_chunks])
        self._vector_store.add(all_chunks, vectors)
        logger.info("Indexed %d chunks", len(all_chunks))

        return IngestionResult(
            articles_ingested=articles_ingested,
            chunks_indexed=len(all_chunks),
        )
