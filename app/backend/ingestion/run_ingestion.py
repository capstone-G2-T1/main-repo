"""
app/backend/ingestion/run_ingestion.py

End-to-end ingestion for one manual:

    process_manual   (extract -> detect language -> translate to Arabic)
    -> chunk_manual  (page-aware overlapping chunks, Arabic text only)
    -> save_chunks   (persist processed chunks to disk, before embedding)
    -> store_manual_chunks (embed -> Chroma vectors + Postgres rows)

Also exposes `run_ingestion_for_directory`, which walks every manual
found by manual_loader.load_manuals() and ingests each one, continuing
past individual failures so one bad manual doesn't stop the batch.
"""

from __future__ import annotations

import logging

from app.backend.ingestion.chunker import chunk_manual, save_chunks
from app.backend.ingestion.manual_processor import process_manual
from app.backend.ingestion.store import IngestionSummary, store_manual_chunks
from app.backend.api.schemas import ManualMetadata

logger = logging.getLogger("run_ingestion")


def ingest_manual(metadata: ManualMetadata) -> IngestionSummary:
    """Run the full extract -> chunk -> embed -> store flow for a single manual."""
    metadata, pages = process_manual(metadata)
    chunks = chunk_manual(pages, metadata)

    # Chunks are saved to disk *before* embedding, so chunking and
    # embedding/storage can be retried independently of one another.
    save_chunks(chunks, manual_name=metadata.file_path)

    return store_manual_chunks(metadata, chunks)


def run_ingestion_for_directory(raw_manuals_dir: str = "data/raw_manuals") -> list[IngestionSummary]:
    """
    Ingest every manual under `raw_manuals_dir` (one subfolder per make,
    per manual_loader's layout). A single manual's failure is logged and
    skipped rather than aborting the whole batch.
    """
    # Local import: manual_loader.py lives at the repo root alongside this
    # package, not inside it -- importing it eagerly at module load time
    # would make `ingestion` depend on being run from that exact layout.
    from manual_loader import load_manuals

    manual_dicts = load_manuals(raw_manuals_dir)
    summaries: list[IngestionSummary] = []

    for entry in manual_dicts:
        metadata = ManualMetadata(**entry)
        try:
            summaries.append(ingest_manual(metadata))
        except Exception:
            logger.exception("Ingestion failed for %s; continuing with next manual", entry.get("file_path"))

    ingested = sum(1 for s in summaries if not s.skipped)
    skipped = sum(1 for s in summaries if s.skipped)
    logger.info("Ingestion run complete: %d ingested, %d skipped (duplicates)", ingested, skipped)
    return summaries


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run_ingestion_for_directory()
