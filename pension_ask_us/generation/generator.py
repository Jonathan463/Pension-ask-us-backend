"""Answer-generation strategies layered on top of retrieval.

Two implementations are provided:

* :class:`ExtractiveGenerator` - no external dependencies; quotes the top
  retrieved chunks. Used as the demo default.
* :class:`OpenAIGenerator` - calls the OpenAI Chat Completions API when an
  API key is configured.

Both honour a strict "answer only from supplied context" instruction to
follow section 8 (Security and Compliance) of the architecture document.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Sequence

from ..schemas import RetrievedChunk

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = (
    "You are a pension knowledge assistant for NHS BSA customer support staff. "
    "Answer the user's question using ONLY the provided article excerpts. "
    "If the answer is not in the excerpts, say you don't know and suggest the "
    "closest related article. Be concise and cite article titles inline."
)


class AnswerGenerator(ABC):
    """Produces a natural-language answer from retrieved chunks."""

    @abstractmethod
    def generate(self, question: str, chunks: Sequence[RetrievedChunk]) -> str: ...


class ExtractiveGenerator(AnswerGenerator):
    """Builds an answer by quoting the most relevant retrieved chunks."""

    def __init__(self, max_excerpts: int = 3, excerpt_chars: int = 400) -> None:
        self._max_excerpts = max_excerpts
        self._excerpt_chars = excerpt_chars

    def generate(self, question: str, chunks: Sequence[RetrievedChunk]) -> str:
        if not chunks:
            return (
                "I couldn't find any matching pension articles for that question. "
                "Try rephrasing or check the NHS BSA knowledge base."
            )

        top = list(chunks)[: self._max_excerpts]
        lines: List[str] = [
            f"Based on {len(top)} relevant article" + ("s" if len(top) != 1 else "") + ":",
            "",
        ]
        for i, rc in enumerate(top, start=1):
            snippet = rc.chunk.text.strip().replace("\n", " ")
            if len(snippet) > self._excerpt_chars:
                snippet = snippet[: self._excerpt_chars].rsplit(" ", 1)[0] + "…"
            lines.append(f"{i}. {rc.chunk.title} (score {rc.score:.2f})")
            lines.append(f"   {snippet}")
            lines.append(f"   Source: {rc.chunk.url}")
            lines.append("")
        return "\n".join(lines).rstrip()


class OpenAIGenerator(AnswerGenerator):
    """LLM-backed generator. Falls back to extractive output on any error."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        fallback: Optional[AnswerGenerator] = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._fallback = fallback or ExtractiveGenerator()
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self._api_key)
        return self._client

    def generate(self, question: str, chunks: Sequence[RetrievedChunk]) -> str:
        if not chunks:
            return self._fallback.generate(question, chunks)

        context_blocks = [
            f"[{i}] Title: {rc.chunk.title}\nURL: {rc.chunk.url}\nContent: {rc.chunk.text}"
            for i, rc in enumerate(chunks, start=1)
        ]
        user_prompt = (
            f"Question: {question}\n\n"
            f"Articles:\n" + "\n\n".join(context_blocks) +
            "\n\nWrite a concise answer and cite the article titles you used."
        )
        try:
            client = self._ensure_client()
            completion = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
            )
            return (completion.choices[0].message.content or "").strip()
        except Exception as exc:
            logger.warning("OpenAI generation failed (%s); using extractive fallback", exc)
            return self._fallback.generate(question, chunks)
