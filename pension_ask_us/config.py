"""Application settings."""
from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_ARTICLE_URLS: List[str] = [
    "https://faq.nhsbsa.nhs.uk/knowledgebase/category/?articlecategory=Annual%20Allowance&id=CAT-01824&parentid=",
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04392/en-us",
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04362/en-us",
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04373/en-us",
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04396/en-us",
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04372/en-us",
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04368/en-us",
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04371/en-us",
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04382/en-us",
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04509/en-us",
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-27957/en-us",
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-02658/en-us",
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04366/en-us",
    "https://www.nhsbsa.nhs.uk/current-processing-times-nhs-pensions",
]


class Settings(BaseSettings):
    """Runtime configuration (overridable via environment variables)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PENSION_",
        extra="ignore",
    )

    # Embedding model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Vector store
    chroma_persist_dir: Path = PROJECT_ROOT / "pension_ask_us" / "data" / "chroma"
    chroma_collection: str = "pension_articles"

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 120

    # Retrieval
    top_k: int = 4

    # HTTP
    http_timeout_seconds: float = 20.0
    http_user_agent: str = "PensionAskUs/0.1 (+demo)"

    # Article sources
    article_urls: List[str] = Field(default_factory=lambda: list(DEFAULT_ARTICLE_URLS))

    # Optional LLM (extractive fallback used when unset)
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"


def get_settings() -> Settings:
    """Factory used as a FastAPI dependency."""
    return Settings()
