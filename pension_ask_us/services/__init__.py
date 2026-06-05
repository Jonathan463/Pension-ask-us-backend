"""Application service layer.

These services encapsulate the use-case orchestration (empty-KB checks,
retrieval -> generation pipelines, ingestion runs) so that transport layers
(FastAPI routes, CLI commands) stay thin.
"""
from .ask_service import AskService
from .ingest_service import IngestService
from .share_service import ShareService

__all__ = ["AskService", "IngestService", "ShareService"]
