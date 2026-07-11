"""Small serialization helpers shared by API logging code."""

from __future__ import annotations

from typing import Any


def build_chunks_summary(chunks: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Keep useful retrieval evidence while avoiding oversized query-log rows."""
    if not chunks:
        return []
    summary = []
    for chunk in chunks:
        metadata = chunk.get("metadata") or {}
        summary.append(
            {
                "id": chunk.get("id"),
                "manual_name": metadata.get("manual_name"),
                "page": metadata.get("page"),
                "section": metadata.get("section"),
                "retrieval_score": chunk.get("retrieval_score"),
                "reranker_score": chunk.get("reranker_score"),
            }
        )
    return summary
