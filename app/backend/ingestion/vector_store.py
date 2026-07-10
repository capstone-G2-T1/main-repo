"""
app/backend/ingestion/vector_store.py

Thin wrapper around the Chroma client, used during ingestion to write
chunk vectors + metadata for a manual. Query-time retrieval
(app/backend/rag/retriever.py) reads from the same collection but is a
separate module -- this file is ingestion-only (write path).

Host/port/collection name default to the same values used in
docker-compose.yml / .env / core/config.py, but are read from the
environment here (rather than importing app.backend.core.config) so the
ingestion package stays independent of the FastAPI app package, same as
the rest of ingestion/*.
"""

from __future__ import annotations

import logging
import os

import chromadb

logger = logging.getLogger("vector_store")

CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "vehicle_manuals_ar")

_client: "chromadb.HttpClient | None" = None


def _get_client() -> "chromadb.HttpClient":
    global _client
    if _client is None:
        _client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    return _client


def _get_collection():
    return _get_client().get_or_create_collection(name=CHROMA_COLLECTION_NAME)


def upsert_chunks(
    ids: list[str],
    embeddings: list[list[float]],
    documents: list[str],
    metadatas: list[dict],
) -> None:
    """
    Insert (or overwrite, by id) chunk vectors + metadata into Chroma.

    Using `upsert` rather than `add` makes re-running ingestion for the
    same manual/chunk_index idempotent instead of erroring on duplicate ids.
    """
    if not ids:
        return

    collection = _get_collection()
    collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
    logger.info(
        "Upserted %d chunk vector(s) into Chroma collection '%s'",
        len(ids), CHROMA_COLLECTION_NAME,
    )


def manual_has_vectors(manual_name: str) -> bool:
    """Secondary dedup guard: True if any vectors already exist for this manual_name."""
    collection = _get_collection()
    result = collection.get(where={"manual_name": manual_name}, limit=1)
    return bool(result.get("ids"))
