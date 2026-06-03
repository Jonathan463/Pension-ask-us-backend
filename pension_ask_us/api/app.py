"""FastAPI application: thin transport layer over the service layer."""
from __future__ import annotations

import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..schemas import (
    AskRequest,
    AskResponse,
    IngestRequest,
    IngestResponse,
)
from ..services import AskService, IngestService
from ..vector_store.store import VectorStore
from . import dependencies as deps
from .exception_handlers import register_exception_handlers

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Pension Ask Us",
        description="AI-powered NHS pension knowledge search (RAG demo)",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)

    @app.get("/health")
    def health(
        vector_store: VectorStore = Depends(deps.get_vector_store),
    ) -> dict:
        return {"status": "ok", "indexed_chunks": vector_store.count()}

    @app.post("/ask", response_model=AskResponse)
    def ask(
        payload: AskRequest,
        service: AskService = Depends(deps.get_ask_service),
    ) -> AskResponse:
        return service.ask(payload.question, top_k=payload.top_k)

    @app.post("/ingest", response_model=IngestResponse)
    def ingest(
        payload: IngestRequest | None = None,
        service: IngestService = Depends(deps.get_ingest_service),
    ) -> IngestResponse:
        urls = payload.urls if payload else None
        return service.ingest(urls=urls)

    return app


app = create_app()
