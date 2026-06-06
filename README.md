# Pension Ask Us — API

AI-powered question-answering over NHS pension knowledge-base articles.
A modular, SOLID-aligned RAG (Retrieval-Augmented Generation) service built
with FastAPI, ChromaDB and Sentence-Transformers.

## What it does

1. **Ingest** — fetches NHSBSA FAQ articles, cleans the HTML, splits them into
   sentence-aware chunks and writes embeddings to a persistent vector store.
2. **Retrieve** — embeds incoming questions and pulls the top-K most similar
   chunks via cosine similarity.
3. **Generate** — composes an answer from those chunks. Uses an OpenAI chat
   model when `PENSION_OPENAI_API_KEY` is set; otherwise falls back to a
   deterministic extractive generator (no external API calls).
4. **Share** — emails an article excerpt to a recipient via SMTP.

## Architecture

Each layer is an interface with a concrete implementation, wired up through a
single composition root (`pension_ask_us/api/dependencies.py`). Swap any
implementation without touching callers.

```
pension_ask_us/
├── api/              FastAPI app + dependency injection
├── services/         Use-case orchestration (AskService, IngestService, ShareService)
├── ingestion/        ArticleSource, Fetcher, HtmlCleaner, TextChunker, Pipeline
├── embeddings/       Embedder ABC + SentenceTransformer implementation
├── vector_store/     VectorStore ABC + Chroma implementation
├── retrieval/        RetrievalService (embed + similarity search)
├── generation/       AnswerGenerator ABC + Extractive / OpenAI implementations
├── email/            EmailSender ABC + SmtpEmailSender implementation
├── exceptions.py     PensionAskUsError hierarchy (mapped to HTTP by handlers)
├── schemas.py        Pydantic DTOs shared across modules
└── config.py         PENSION_-prefixed pydantic-settings
```

## Quickstart

### Prerequisites
- Python 3.11+ (the Docker image uses 3.11)
- `pip` and a network connection on first run (the embedding model is ~91 MB)

### Install and run

```bash
pip install -r requirements.txt

# 1) Build the index (one-off, takes ~30s end-to-end)
python main.py ingest

# 2) Start the API
python main.py serve                            # binds 127.0.0.1:8000
python main.py serve --host 0.0.0.0 --port 8000

# 3) (Optional) Ask from the CLI without starting the server
python main.py ask "How much do I contribute to my NHS pension?"
```

Swagger UI is available at <http://localhost:8000/docs>.

## Configuration

All settings are environment variables with the `PENSION_` prefix
(also readable from a `.env` file at the repo root). See `.env.example`
for the full list. The most useful ones:

| Variable | Default | Purpose |
|---|---|---|
| `PENSION_CHROMA_PERSIST_DIR` | `pension_ask_us/data/chroma` | Where the vector index lives. Override to mount a volume. |
| `PENSION_TOP_K` | `4` | Default number of chunks returned per question. |
| `PENSION_OPENAI_API_KEY` | _(unset)_ | Optional. Enables the OpenAI generator; falls back to extractive when blank. |
| `PENSION_OPENAI_MODEL` | `gpt-4o-mini` | Chat model used when `PENSION_OPENAI_API_KEY` is set. |
| `PENSION_EMAIL_FROM`, `PENSION_SMTP_*` | _(unset)_ | SMTP for `POST /share`. See `.env.example` for the Gmail pattern. |

## API

| Method | Path | Body | Notes |
|---|---|---|---|
| `GET` | `/health` | — | `{"status":"ok","indexed_chunks":N}` |
| `POST` | `/ask` | `{question, top_k?}` | Returns `{question, answer, sources[]}` |
| `POST` | `/ingest` | `{urls?}` | Rebuilds the index. Empty body uses the configured URLs. |
| `POST` | `/share` | `{recipient, question, article_title, article_url, note?}` | Emails the article excerpt via SMTP. |

Errors follow a consistent JSON contract:

```json
{ "error": "empty_knowledge_base", "message": "Knowledge base is empty…", "details": {} }
```

Common codes: `empty_knowledge_base` (409), `invalid_question` (422),
`ingestion_failed` (502), `email_send_failed` (502), `vector_store_error` (500).

## Docker

```bash
docker build -t pension-ask-us-api .

docker run --rm -p 8000:8000 \
  -v pension_chroma:/data/chroma \
  -e PENSION_CHROMA_PERSIST_DIR=/data/chroma \
  pension-ask-us-api
```

The image installs the **CPU-only PyTorch wheel** (no CUDA bloat) and
pre-downloads the embedding model at build time, so the first `/ask` is fast.

## Frontend

The React SPA lives in a separate repository:
**[`pension-ask-us-web`](https://github.com/Jonathan463/Pension-ask-us)** — deploys independently and
points at this API via `VITE_API_BASE_URL`.

## License

See [`LICENSE`](./LICENSE).
