# Backend image for the Pension Ask Us FastAPI service.
#
# Build:  docker build -t pension-ask-us-api .
# Run:    docker run --rm -p 8000:8000 \
#             -v pension_chroma:/data/chroma \
#             -e PENSION_CHROMA_PERSIST_DIR=/data/chroma \
#             pension-ask-us-api
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=180 \
    PIP_RETRIES=5 \
    HF_HOME=/opt/hf-cache

WORKDIR /app

# Build deps required by chromadb / sentence-transformers transitives.
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential curl \
 && rm -rf /var/lib/apt/lists/*

# Install the CPU-only PyTorch build first so sentence-transformers picks it
# up instead of pulling ~2GB of CUDA wheels from PyPI's default index.
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch

COPY requirements.txt ./
RUN pip install -r requirements.txt

# Application code (kept separate from deps so source edits don't bust pip layer).
COPY main.py ./
COPY pension_ask_us ./pension_ask_us

# Pre-download the embedding model into the image so the first /ask call
# doesn't pay a model-download cost.
RUN python -c "from sentence_transformers import SentenceTransformer; \
SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Run as non-root.
RUN useradd --create-home --uid 1001 app \
 && mkdir -p /data/chroma \
 && chown -R app:app /app /data /opt/hf-cache
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

CMD ["python", "main.py", "serve", "--host", "0.0.0.0", "--port", "8000"]
