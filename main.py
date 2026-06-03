"""Demo entrypoint for the Pension Ask Us RAG service.

Usage:
    python main.py ingest          # fetch + index the configured articles
    python main.py serve           # start the FastAPI server on :8000
    python main.py ask "question"  # ask without starting the server
"""
from __future__ import annotations

import argparse
import logging
import sys

from pension_ask_us.api import dependencies as deps
from pension_ask_us.exceptions import (
    EmptyKnowledgeBaseError,
    PensionAskUsError,
)

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    )


def cmd_ingest() -> int:
    result = deps.get_ingest_service().ingest()
    print(
        f"Ingested {result.articles_ingested} articles "
        f"-> {result.chunks_indexed} chunks indexed."
    )
    return 0


def cmd_serve(host: str, port: int) -> int:
    import uvicorn

    uvicorn.run("pension_ask_us.api.app:app", host=host, port=port, reload=False)
    return 0


def cmd_ask(question: str) -> int:
    response = deps.get_ask_service().ask(question)
    print(f"Q: {response.question}\n")
    print(response.answer)
    print("\nSources:")
    for src in response.sources:
        print(f"  - {src.title} ({src.score:.2f}) :: {src.url}")
    return 0


def _handle_app_error(exc: PensionAskUsError) -> int:
    """Single CLI translator for any application error."""
    hint = ""
    if isinstance(exc, EmptyKnowledgeBaseError):
        hint = " Run `python main.py ingest` first."
    print(f"[{exc.error_code}] {exc.message}{hint}", file=sys.stderr)
    return 1 if exc.status_code < 500 else 2


def _dispatch(args: argparse.Namespace) -> int:
    if args.command == "ingest":
        return cmd_ingest()
    if args.command == "serve":
        return cmd_serve(args.host, args.port)
    if args.command == "ask":
        return cmd_ask(" ".join(args.question))
    return 2


def main(argv: list[str] | None = None) -> int:
    _configure_logging()
    parser = argparse.ArgumentParser(description="Pension Ask Us demo CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ingest", help="Fetch and index the configured articles")

    serve_p = sub.add_parser("serve", help="Run the FastAPI server")
    serve_p.add_argument("--host", default="127.0.0.1")
    serve_p.add_argument("--port", type=int, default=8000)

    ask_p = sub.add_parser("ask", help="Ask a question from the CLI")
    ask_p.add_argument("question", nargs="+")

    args = parser.parse_args(argv)
    try:
        return _dispatch(args)
    except PensionAskUsError as exc:
        return _handle_app_error(exc)
    except Exception:  # noqa: BLE001 - last-resort logger
        logger.exception("Unexpected error running command %s", args.command)
        return 2


if __name__ == "__main__":
    sys.exit(main())
