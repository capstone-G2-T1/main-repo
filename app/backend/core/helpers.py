"""
app/backend/core/helpers.py

Helper functions for the Vehicle Manual RAG backend.
"""

def _build_chunks_summary(chunks: list | None) -> list[dict]:
    """
    Build a lightweight summary of retrieved chunks for logging.

    Safe to call even if the pipeline doesn't yet expose retrieval results.
    """
    if not chunks:
        return []

    summary = []

    for chunk in chunks:
        summary.append(
            {
                "manual": chunk.get("manual"),
                "page": chunk.get("page"),
                "score": chunk.get("score"),
            }
        )

    return summary