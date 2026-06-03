"""Use-case service for running the article ingestion pipeline."""
from __future__ import annotations

from typing import Callable, Optional, Sequence

from ..exceptions import IngestionFailedError
from ..ingestion.pipeline import IngestionPipeline
from ..ingestion.sources import ArticleSource, StaticUrlSource
from ..schemas import IngestResponse


PipelineFactory = Callable[[Optional[ArticleSource]], IngestionPipeline]


class IngestService:
    """Runs the ingestion pipeline, optionally against caller-supplied URLs.

    A factory is injected (rather than a concrete pipeline) so each call
    builds a fresh pipeline configured for the requested source. This keeps
    the service decoupled from how pipelines are constructed.
    """

    def __init__(self, pipeline_factory: PipelineFactory) -> None:
        self._pipeline_factory = pipeline_factory

    def ingest(self, urls: Optional[Sequence[str]] = None) -> IngestResponse:
        source: Optional[ArticleSource] = (
            StaticUrlSource(urls) if urls else None
        )
        pipeline = self._pipeline_factory(source)
        result = pipeline.run(reset=True)
        if result.articles_ingested == 0:
            raise IngestionFailedError(
                "Ingestion produced no usable articles.",
                details={"requested_urls": len(list(urls)) if urls else None},
            )
        return IngestResponse(
            articles_ingested=result.articles_ingested,
            chunks_indexed=result.chunks_indexed,
        )
