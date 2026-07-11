"""Optional lazy cross-encoder reranking."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, Callable

from core.config import settings
from rag.types import RetrievedChunk

logger = logging.getLogger("rag.reranker")


@lru_cache(maxsize=1)
def _get_model() -> Any:
    from sentence_transformers import CrossEncoder

    logger.info("Loading reranker model: %s", settings.RERANKER_MODEL)
    return CrossEncoder(settings.RERANKER_MODEL)


def rerank_chunks(
    query: str,
    chunks: list[RetrievedChunk],
    top_k: int | None = None,
    *,
    enabled: bool | None = None,
    model_getter: Callable[[], Any] = _get_model,
) -> list[RetrievedChunk]:
    """Rerank candidates or preserve retrieval order when disabled/unavailable."""
    if not chunks:
        return []
    limit = top_k or settings.RERANKER_TOP_K
    use_reranker = settings.RERANKER_ENABLED if enabled is None else enabled
    if not use_reranker:
        return chunks[:limit]

    try:
        scores = model_getter().predict([(query, chunk.text) for chunk in chunks])
        if len(scores) != len(chunks):
            raise ValueError("reranker returned an unexpected score count")
        for chunk, score in zip(chunks, scores):
            chunk.reranker_score = float(score)
        return sorted(chunks, key=lambda chunk: chunk.reranker_score or float("-inf"), reverse=True)[:limit]
    except Exception as exc:  # optional dependency/model boundary
        logger.error("Reranking unavailable; preserving retrieval order: %s", exc.__class__.__name__)
        return chunks[:limit]
