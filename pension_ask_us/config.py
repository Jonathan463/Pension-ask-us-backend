"""Application settings."""
from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_ARTICLE_URLS: List[str] = [
    # --- Account, membership, online services (5) ---
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04454/en-us",  # Where can I find my membership number?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-28696/en-us",  # How do I register for My NHS Pension?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04244/en-us",  # How can I get an estimate of my NHS pension benefits?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-02755/en-us",  # How can I access my Total Reward Statement (TRS)?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-02726/en-us",  # What is a Total Reward Statement (TRS)?

    # --- Joining / opting out (3) ---
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04447/en-us",  # Who can join the NHS Pension Scheme?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-27795/en-us",  # How do I opt out of the NHS Pension Scheme?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04551/en-us",  # How do I request a membership statement?

    # --- Contributions (5) ---
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04392/en-us",  # What are pension contributions?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04362/en-us",  # Which payments are pensionable?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04372/en-us",  # What is salary sacrifice?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04509/en-us",  # Can I get a refund of my NHS pension contributions?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04480/en-us",  # Can I pay pension contributions while on sick leave?

    # --- Annual Allowance (5) ---
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-05035/en-us",  # What is annual allowance (AA)?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-05041/en-us",  # What is the annual allowance (AA) charge?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-05029/en-us",  # What is tapered annual allowance (AA)?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-05031/en-us",  # What is money purchase annual allowance?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-05067/en-us",  # How is my NHS Pension benefit growth calculated for AA?

    # --- Lifetime allowance / tax (2) ---
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-05015/en-us",  # What is lifetime allowance (LTA)?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-05006/en-us",  # What affected my LTA calculation?

    # --- Increasing your pension (AVCs, AP, added years) (3) ---
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04929/en-us",  # What is additional pension (AP)?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04958/en-us",  # What are added years (AY)?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04123/en-us",  # What are money purchase AVCs (MPAVC)?

    # --- Retirement, abatement, ERRBO (4) ---
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04177/en-us",  # What is abatement?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04170/en-us",  # How is abatement calculated?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04128/en-us",  # What is early retirement reduction buy out (ERRBO)?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04108/en-us",  # What does 'recycling lump sums' mean?

    # --- Ill health (3) ---
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-05113/en-us",  # Can I take my pension on the grounds of ill health?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-05114/en-us",  # What is the process for an ill health application?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-05130/en-us",  # What is a Tier 1 and Tier 2 ill health pension?

    # --- Death benefits & nominations (3) ---
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-31056/en-us",  # How do I make a nomination for an adult dependant's pension?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04993/en-us",  # What is an adult dependant's pension?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04188/en-us",  # Will you accept an interim death certificate?

    # --- Transfers in/out (3) ---
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04275/en-us",  # Can I transfer other pension benefits into the NHS Pension Scheme?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04283/en-us",  # Can I transfer my pension benefits out of the NHS Pension Scheme?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-04274/en-us",  # How do I transfer pension benefits into the NHS Pension Scheme?

    # --- McCloud / 2015 remedy (3) ---
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-25794/en-us",  # What is the public service pensions remedy (McCloud)?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-29194/en-us",  # What is a Remediable Service Statement (RSS)?
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-28944/en-us",  # What is rollback of remedy period service?

    # --- Life events / operational (2) ---
    "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-05155/en-us",  # What is pension sharing? (divorce)
    "https://www.nhsbsa.nhs.uk/current-processing-times-nhs-pensions",  # Operational SLAs (off-portal)
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

    # Email delivery (used by POST /share)
    email_mode: str = "console"
    email_from: str | None = None
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True


def get_settings() -> Settings:
    """Factory used as a FastAPI dependency."""
    return Settings()
