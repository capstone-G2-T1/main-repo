"""Query-time Chroma retrieval using the ingestion embedding space."""

from __future__ import annotations

import logging
from typing import Any, Callable

from core.config import settings
from rag.types import RetrievedChunk

logger = logging.getLogger("rag.retriever")


def _default_embed(text: str) -> list[float]:
    # Lazy import keeps the optional ML dependency out of API startup.
    from ingestion.embedder import embed_texts

    vectors = embed_texts([text])
    return vectors[0] if vectors else []


def _default_collection():
    from ingestion.vector_store import _get_collection

    return _get_collection()


def _first_batch(value: Any) -> list[Any]:
    if not isinstance(value, list) or not value:
        return []
    return value[0] if isinstance(value[0], list) else value


def retrieve_chunks(
    query: str,
    metadata_filter: dict | None = None,
    top_k: int | None = None,
    *,
    collection_getter: Callable[[], Any] = _default_collection,
    embedder: Callable[[str], list[float]] = _default_embed,
) -> list[RetrievedChunk]:
    """Retrieve candidate chunks, returning an empty list on service failures."""
    if not query.strip():
        return []

    limit = top_k or settings.RETRIEVAL_TOP_K
    try:
        embedding = embedder(query)
        if not embedding:
            return []
        kwargs: dict[str, Any] = {
            "query_embeddings": [embedding],
            "n_results": limit,
            "include": ["documents", "metadatas", "distances"],
        }
        if metadata_filter:
            kwargs["where"] = metadata_filter
        result = collection_getter().query(**kwargs)
    except Exception as exc:  # external service and optional model boundary
        logger.error("Chroma retrieval failed: %s", exc.__class__.__name__)
        return []

    ids = _first_batch(result.get("ids")) if isinstance(result, dict) else []
    documents = _first_batch(result.get("documents")) if isinstance(result, dict) else []
    metadatas = _first_batch(result.get("metadatas")) if isinstance(result, dict) else []
    distances = _first_batch(result.get("distances")) if isinstance(result, dict) else []

    chunks: list[RetrievedChunk] = []
    for index, chunk_id in enumerate(ids[:limit]):
        text = documents[index] if index < len(documents) and documents[index] else ""
        metadata = metadatas[index] if index < len(metadatas) and isinstance(metadatas[index], dict) else {}
        distance = distances[index] if index < len(distances) else None
        try:
            score = None if distance is None else 1.0 / (1.0 + max(float(distance), 0.0))
        except (TypeError, ValueError):
            score = None
        chunks.append(RetrievedChunk(str(chunk_id), str(text), metadata, score))
    return chunks
