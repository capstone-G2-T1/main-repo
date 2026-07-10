"""
app/backend/ingestion/store.py

Embeds a manual's chunks and stores them in both Chroma (vectors +
metadata filters) and Postgres (vehicle/manual/chunk records), skipping
manuals that have already been ingested so re-running ingestion is safe.

This module deliberately reuses the existing SQLAlchemy models/session
from app.backend.db (the real Postgres schema) rather than re-defining
storage separately -- unlike translation, storage has no query-time-leak
concern, so sharing the schema definitions here is the right trade-off.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path

from app.backend.db.models import Manual, ManualChunk, Vehicle
from app.backend.db.session import SessionLocal
from app.backend.ingestion.chunker import Chunk
from app.backend.ingestion.embedder import embed_texts
from app.backend.ingestion.vector_store import upsert_chunks
from app.backend.api.schemas import ManualMetadata

logger = logging.getLogger("store")


@dataclass
class IngestionSummary:
    """Result of attempting to ingest one manual, returned to the caller/script."""

    manual_name: str
    skipped: bool = False
    reason: str | None = None
    chunk_count: int = 0
    vehicle_id: str | None = None
    manual_id: str | None = None


def _file_checksum(path: str | Path) -> str:
    """SHA-256 of the PDF bytes -- the dedup key for a manual (matches manuals.checksum)."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            sha256.update(block)
    return sha256.hexdigest()


def _parse_year(year: str | None) -> int:
    """Vehicle.year is a single SMALLINT; a "2020-2023" range uses its first year."""
    if not year:
        return 0
    return int(year.split("-")[0])


def _get_or_create_vehicle(db, make: str, model: str, year: str | None) -> Vehicle:
    year_int = _parse_year(year)
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.make == make, Vehicle.model == model, Vehicle.year == year_int)
        .first()
    )
    if vehicle is None:
        vehicle = Vehicle(make=make, model=model, trim=None, year=year_int)
        db.add(vehicle)
        db.flush()  # assigns vehicle.id without committing the transaction yet
    return vehicle


def store_manual_chunks(metadata: ManualMetadata, chunks: list[Chunk]) -> IngestionSummary:
    """
    Embed + store `chunks` for one manual.

    Dedup: if a manual with the same file checksum already exists in
    Postgres, ingestion is skipped entirely -- no embeddings are computed
    and nothing is written to Chroma or Postgres.
    """
    manual_name = Path(metadata.file_path).name
    checksum = _file_checksum(metadata.file_path)

    db = SessionLocal()
    try:
        existing = db.query(Manual).filter(Manual.checksum == checksum).first()
        if existing:
            logger.info("Manual %s already ingested (checksum match); skipping", manual_name)
            return IngestionSummary(
                manual_name=manual_name,
                skipped=True,
                reason="duplicate checksum",
                manual_id=str(existing.id),
                vehicle_id=str(existing.vehicle_id),
            )

        vehicle = _get_or_create_vehicle(db, metadata.make, metadata.model, metadata.year)

        manual_row = Manual(
            vehicle_id=vehicle.id,
            manual_name=manual_name,
            language=metadata.language,
            checksum=checksum,
            is_translated=metadata.is_translated,
            source_path=metadata.file_path,
            translated_path=metadata.translated_path,
            total_pages=metadata.total_pages,
        )
        db.add(manual_row)
        db.flush()  # assigns manual_row.id, needed to build Chroma vector ids below

        if chunks:
            texts = [c.text for c in chunks]
            embeddings = embed_texts(texts)
            ids = [f"{manual_row.id}:{c.chunk_index}" for c in chunks]

            metadatas = [
                {
                    "make": c.make,
                    "model": c.model,
                    "year": c.year or "",
                    "page": c.page_number,
                    "language": c.language,
                    "manual_name": c.manual_name,
                    "section": c.section or "",
                }
                for c in chunks
            ]

            # Vectors go to Chroma first; if this fails the whole call
            # raises before anything is committed to Postgres below, so
            # a failed embed/upsert never leaves an orphaned manual row.
            upsert_chunks(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

            for chunk, vector_id in zip(chunks, ids):
                db.add(
                    ManualChunk(
                        manual_id=manual_row.id,
                        chunk_index=chunk.chunk_index,
                        page_number=chunk.page_number,
                        section=chunk.section,
                        chunk_text=chunk.text,
                        chroma_vector_id=vector_id,
                    )
                )

        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to store manual %s; rolled back Postgres changes", manual_name)
        raise
    finally:
        db.close()

    logger.info("Stored %d chunk(s) for %s", len(chunks), manual_name)
    return IngestionSummary(
        manual_name=manual_name,
        skipped=False,
        chunk_count=len(chunks),
        vehicle_id=str(vehicle.id),
        manual_id=str(manual_row.id),
    )
