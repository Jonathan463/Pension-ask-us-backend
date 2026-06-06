"""Vector store abstractions and a ChromaDB implementation."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Sequence

from ..embeddings.embedder import Vector
from ..exceptions import VectorStoreError
from ..schemas import Chunk, RetrievedChunk


class VectorStore(ABC):
    """Persists chunk embeddings and performs similarity search."""

    @abstractmethod
    def add(self, chunks: Sequence[Chunk], vectors: Sequence[Vector]) -> None: ...

    @abstractmethod
    def query(self, vector: Vector, top_k: int) -> List[RetrievedChunk]: ...

    @abstractmethod
    def reset(self) -> None: ...

    @abstractmethod
    def count(self) -> int: ...


class ChromaVectorStore(VectorStore):
    """Persistent ChromaDB-backed vector store."""

    def __init__(self, persist_dir: Path, collection_name: str) -> None:
        try:
            import chromadb

            persist_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(persist_dir))
            self._collection_name = collection_name
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            raise VectorStoreError(
                "Failed to initialise ChromaDB.",
                details={"path": str(persist_dir), "cause": str(exc)},
            ) from exc

    def add(self, chunks: Sequence[Chunk], vectors: Sequence[Vector]) -> None:
        if not chunks:
            return
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have the same length")
        try:
            self._collection.add(
                ids=[c.id for c in chunks],
                embeddings=list(vectors),
                documents=[c.text for c in chunks],
                metadatas=[
                    {"url": c.url, "title": c.title, "position": c.position}
                    for c in chunks
                ],
            )
        except Exception as exc:
            raise VectorStoreError(
                "Failed to add chunks to the vector store.",
                details={"count": len(chunks), "cause": str(exc)},
            ) from exc

    def query(self, vector: Vector, top_k: int) -> List[RetrievedChunk]:
        if top_k <= 0:
            return []
        try:
            result = self._collection.query(
                query_embeddings=[list(vector)],
                n_results=top_k,
            )
        except Exception as exc:
            raise VectorStoreError(
                "Failed to query the vector store.",
                details={"top_k": top_k, "cause": str(exc)},
            ) from exc

        ids = (result.get("ids") or [[]])[0]
        docs = (result.get("documents") or [[]])[0]
        metas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        retrieved: List[RetrievedChunk] = []
        for chunk_id, doc, meta, distance in zip(ids, docs, metas, distances):
            meta = meta or {}
            chunk = Chunk(
                id=chunk_id,
                url=str(meta.get("url", "")),
                title=str(meta.get("title", "")),
                text=doc or "",
                position=int(meta.get("position", 0)),
            )
            score = max(0.0, 1.0 - float(distance))
            retrieved.append(RetrievedChunk(chunk=chunk, score=score))
        return retrieved

    def reset(self) -> None:
        try:
            self._client.delete_collection(self._collection_name)
        except Exception:
            pass
        try:
            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            raise VectorStoreError(
                "Failed to recreate the vector store collection.",
                details={"collection": self._collection_name, "cause": str(exc)},
            ) from exc

    def count(self) -> int:
        return int(self._collection.count())
