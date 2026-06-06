"""Abstractions and implementations for text embedding."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Sequence

from ..exceptions import EmbeddingError


Vector = List[float]


class Embedder(ABC):
    """Encodes text into dense vectors."""

    @abstractmethod
    def embed(self, texts: Sequence[str]) -> List[Vector]:
        """Embed a batch of texts."""

    def embed_one(self, text: str) -> Vector:
        return self.embed([text])[0]


class SentenceTransformerEmbedder(Embedder):
    """Local SentenceTransformer-based embedder.

    The model is loaded lazily so importing this module does not pull the
    weights into memory until they are actually needed.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self._model_name = model_name
        self._model = None

    def _ensure_loaded(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self._model_name)
            except Exception as exc:
                raise EmbeddingError(
                    f"Failed to load embedding model '{self._model_name}'",
                    details={"cause": str(exc)},
                ) from exc
        return self._model

    def embed(self, texts: Sequence[str]) -> List[Vector]:
        if not texts:
            return []
        model = self._ensure_loaded()
        try:
            vectors = model.encode(
                list(texts),
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
        except Exception as exc:
            raise EmbeddingError(
                "Failed to embed texts.",
                details={"batch_size": len(texts), "cause": str(exc)},
            ) from exc
        return vectors.tolist()
