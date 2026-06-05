"""Composition root: build collaborators from settings and cache them.

Centralising construction here keeps the FastAPI routes free of concrete
imports (Dependency Inversion). Tests can replace any of the factories.
"""
from __future__ import annotations

from functools import lru_cache

from ..config import Settings, get_settings
from ..email import EmailSender, SmtpEmailSender
from ..exceptions import EmailNotConfiguredError
from ..embeddings.embedder import Embedder, SentenceTransformerEmbedder
from ..generation.generator import (
    AnswerGenerator,
    ExtractiveGenerator,
    OpenAIGenerator,
)
from ..ingestion.chunker import TextChunker
from ..ingestion.cleaner import HtmlCleaner
from ..ingestion.fetcher import ArticleFetcher, HttpArticleFetcher
from ..ingestion.pipeline import IngestionPipeline
from ..ingestion.sources import ArticleSource, StaticUrlSource
from ..retrieval.service import RetrievalService
from ..services import AskService, IngestService, ShareService
from ..vector_store.store import ChromaVectorStore, VectorStore


@lru_cache(maxsize=1)
def _settings() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    return SentenceTransformerEmbedder(_settings().embedding_model)


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    s = _settings()
    return ChromaVectorStore(
        persist_dir=s.chroma_persist_dir,
        collection_name=s.chroma_collection,
    )


@lru_cache(maxsize=1)
def get_retrieval_service() -> RetrievalService:
    s = _settings()
    return RetrievalService(
        embedder=get_embedder(),
        vector_store=get_vector_store(),
        default_top_k=s.top_k,
    )


@lru_cache(maxsize=1)
def get_generator() -> AnswerGenerator:
    s = _settings()
    if s.openai_api_key:
        return OpenAIGenerator(api_key=s.openai_api_key, model=s.openai_model)
    return ExtractiveGenerator()


def build_fetcher() -> ArticleFetcher:
    s = _settings()
    return HttpArticleFetcher(
        timeout_seconds=s.http_timeout_seconds,
        user_agent=s.http_user_agent,
    )


def build_ingestion_pipeline(source: ArticleSource | None = None) -> IngestionPipeline:
    s = _settings()
    return IngestionPipeline(
        source=source or StaticUrlSource(s.article_urls),
        fetcher=build_fetcher(),
        cleaner=HtmlCleaner(),
        chunker=TextChunker(
            chunk_size=s.chunk_size,
            chunk_overlap=s.chunk_overlap,
        ),
        embedder=get_embedder(),
        vector_store=get_vector_store(),
    )


@lru_cache(maxsize=1)
def get_ask_service() -> AskService:
    return AskService(
        retrieval=get_retrieval_service(),
        generator=get_generator(),
        vector_store=get_vector_store(),
    )


@lru_cache(maxsize=1)
def get_ingest_service() -> IngestService:
    return IngestService(pipeline_factory=build_ingestion_pipeline)


@lru_cache(maxsize=1)
def get_email_sender() -> EmailSender:
    s = _settings()
    if not (s.smtp_username and s.smtp_password):
        raise EmailNotConfiguredError(
            "SMTP credentials are not configured. Set PENSION_SMTP_USERNAME "
            "and PENSION_SMTP_PASSWORD in your environment.",
        )
    return SmtpEmailSender(
        host=s.smtp_host,
        port=s.smtp_port,
        username=s.smtp_username,
        password=s.smtp_password,
        use_tls=s.smtp_use_tls,
    )


@lru_cache(maxsize=1)
def get_share_service() -> ShareService:
    s = _settings()
    from_address = s.email_from or s.smtp_username or ""
    return ShareService(
        sender=get_email_sender(),
        from_address=from_address,
    )
