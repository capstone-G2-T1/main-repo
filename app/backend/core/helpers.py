
# Helper — build retrieved_chunks_summary

def _build_chunks_summary(chunks: list[dict] | None) -> list[dict] | None:
    """
    Returns metadata + first 200 chars of text for each chunk.
    Returns None safely when chunks is empty or None.
    """
    if not chunks:
        return None

    summary = []
    for chunk in chunks:
        summary.append({
            "manual_name": chunk.get("manual_name"),
            "page":        chunk.get("page"),
            "section":     chunk.get("section"),
            "score":       chunk.get("score"),
            "text_preview": (chunk.get("text") or "")[:200],
        })
    return summary