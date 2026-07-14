"""Optional lazy cross-encoder reranking."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, Callable

from core.config import settings
from rag.metadata import chunk_stable_id
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
    rerank_chunks.last_fallback_used = False
    if not chunks:
        return []
    limit = top_k or settings.RERANKER_TOP_K
    deduped: list[RetrievedChunk] = []
    seen: set[str] = set()
    for chunk in chunks:
        stable_id = chunk_stable_id(chunk.id, chunk.text, chunk.metadata)
        if stable_id not in seen:
            seen.add(stable_id)
            deduped.append(chunk)
    use_reranker = settings.RERANKER_ENABLED if enabled is None else enabled
    if not use_reranker:
        return deduped[:limit]

    try:
        pairs = [(query, chunk.text) for chunk in deduped]
        scores = model_getter().predict(pairs)
        if len(scores) != len(deduped):
            raise ValueError("reranker returned an unexpected score count")
        for chunk, score in zip(deduped, scores):
            chunk.reranker_score = float(score)
            if chunk.reranker_score != chunk.reranker_score:
                raise ValueError("reranker returned NaN score")
        return sorted(deduped, key=lambda chunk: chunk.reranker_score if chunk.reranker_score is not None else float("-inf"), reverse=True)[:limit]
    except Exception as exc:  # optional dependency/model boundary
        rerank_chunks.last_fallback_used = True
        logger.error("Reranking unavailable; preserving retrieval order: %s: %s", exc.__class__.__name__, exc)
        return deduped[:limit]


rerank_chunks.last_fallback_used = False
