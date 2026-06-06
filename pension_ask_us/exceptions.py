"""Application-wide exception hierarchy.

Every error raised by the application inherits from :class:`PensionAskUsError`
and carries its own ``status_code`` and ``error_code``. Transport layers
(FastAPI, CLI) register a single handler against the base class and translate
any subclass into the appropriate response, so the routes themselves stay
free of try/except blocks.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


class PensionAskUsError(Exception):
    """Base class for all application errors."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(
        self,
        message: str = "",
        *,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message or self.__doc__ or self.error_code)
        self.message = str(self)
        self.details: Dict[str, Any] = dict(details or {})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ServiceError(PensionAskUsError):
    """Base class for use-case / domain errors."""

    status_code = 400
    error_code = "service_error"


class EmptyKnowledgeBaseError(ServiceError):
    """The knowledge base contains no chunks; ingestion has not been run."""

    status_code = 409
    error_code = "empty_knowledge_base"


class InvalidQuestionError(ServiceError):
    """The supplied question is empty or blank."""

    status_code = 400
    error_code = "invalid_question"


class IngestionFailedError(ServiceError):
    """Ingestion completed but produced zero usable articles."""

    status_code = 502
    error_code = "ingestion_failed"


class InvalidEmailError(ServiceError):
    """The supplied recipient address is missing or malformed."""

    status_code = 400
    error_code = "invalid_email"


class NoArticleToShareError(ServiceError):
    """The /ask response had no top article available to share."""

    status_code = 409
    error_code = "no_article_to_share"


class EmailDeliveryError(PensionAskUsError):
    """The configured email backend failed to send the message."""

    status_code = 502
    error_code = "email_delivery_failed"


class EmailNotConfiguredError(PensionAskUsError):
    """SMTP credentials are missing from configuration."""

    status_code = 503
    error_code = "email_not_configured"


class IngestionError(PensionAskUsError):
    """Base class for errors raised inside the ingestion pipeline."""

    status_code = 500
    error_code = "ingestion_error"


class ArticleFetchError(IngestionError):
    """A single article URL could not be retrieved.

    This is normally caught at the pipeline boundary so one bad URL does
    not abort the whole ingestion run.
    """

    status_code = 502
    error_code = "article_fetch_failed"


class VectorStoreError(PensionAskUsError):
    """The vector store backend failed."""

    status_code = 503
    error_code = "vector_store_error"


class EmbeddingError(PensionAskUsError):
    """The embedding model failed."""

    status_code = 503
    error_code = "embedding_error"
