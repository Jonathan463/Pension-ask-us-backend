"""Centralised FastAPI exception handlers.

Registering handlers against the base classes in
:mod:`pension_ask_us.exceptions` removes the need for try/except blocks in
individual route handlers. Any subclass is matched automatically because
FastAPI walks the MRO when looking up a handler.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ..exceptions import PensionAskUsError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all application exception handlers to ``app``."""

    @app.exception_handler(PensionAskUsError)
    async def handle_app_error(
        request: Request, exc: PensionAskUsError
    ) -> JSONResponse:
        log = logger.warning if exc.status_code < 500 else logger.error
        log(
            "%s on %s %s: %s",
            exc.__class__.__name__,
            request.method,
            request.url.path,
            exc.message,
        )
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(Exception)
    async def handle_unexpected(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "Unhandled exception on %s %s", request.method, request.url.path
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "An unexpected error occurred.",
                "details": {},
            },
        )
