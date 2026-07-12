"""
Subset smoke test for the real ingestion pipeline (app/backend/ingestion/run_ingestion.py).

run_ingestion.ingest_manual() processes a manual's ENTIRE page set, and English
manuals get every page translated through Ollama -- for a 202-page manual like
BYD_DOLPHIN_2025.pdf that's 200+ blocking translation calls, likely 1+ hours on
this CPU-only Ollama setup. This script exercises the exact same pipeline stages
(pdf_parser -> language_detector -> translator -> chunker -> store) but truncates
to the first PAGE_LIMIT pages first, so the full pipeline can be validated in
minutes before committing to a full-manual run.

Not a pytest test -- run it directly so its prints are visible:

    python scripts/test_ingestion_subset.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Windows consoles default to cp1252, which can't encode Arabic output.
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "app" / "backend"
for path in (str(BACKEND), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

# This runs on the host, not inside the compose network, so it needs the
# host-published ports/names rather than the in-network service names from .env.
os.environ.setdefault("CHROMA_HOST", "localhost")
os.environ.setdefault("CHROMA_PORT", "8001")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("OLLAMA_HOST", "http://localhost:11434")
os.environ.setdefault("OLLAMA_MODEL", "qwen2.5:7b-instruct")
os.environ["DEBUG"] = "false"

from ingestion.chunker import chunk_manual, save_chunks  # noqa: E402
from ingestion.language_detector import detect_manual_language  # noqa: E402
from manual_loader import _parse_manual  # noqa: E402
from ingestion.pdf_parser import extract_pdf_pages  # noqa: E402
from ingestion.store import store_manual_chunks  # noqa: E402
from ingestion.translator import save_translated_manual, translate_pages  # noqa: E402
from ingestion.vector_store import _get_client  # noqa: E402
from db.models import Manual  # noqa: E402
from db.session import SessionLocal  # noqa: E402

PDF_PATH = ROOT / "data" / "raw_manuals" / "BYD" / "BYD_DOLPHIN_2025.pdf"
PAGE_LIMIT = 5


def main() -> None:
    print(f"PDF: {PDF_PATH}")
    print(f"Chroma:   localhost:{os.environ['CHROMA_PORT']}")
    print(f"Postgres: {os.environ['POSTGRES_HOST']}")
    print(f"Ollama:   {os.environ['OLLAMA_HOST']} (model={os.environ['OLLAMA_MODEL']})")
    print(f"Page limit for this smoke run: {PAGE_LIMIT} (real file has 202 pages)\n")

    metadata = _parse_manual(PDF_PATH, make_folder="BYD")
    print(f"1. Parsed metadata: make={metadata.make} model={metadata.model} year={metadata.year}\n")

    print("2. Extracting PDF text...")
    extraction = extract_pdf_pages(PDF_PATH)
    metadata.total_pages = extraction.total_pages
    metadata.ocr_page_count = extraction.ocr_page_count
    metadata.extraction_errors = extraction.errors
    pages = extraction.pages[:PAGE_LIMIT]
    print(f"   Extracted {extraction.total_pages} page(s) total; using first {len(pages)} for this run.\n")

    metadata.language = detect_manual_language(page.text for page in pages)
    print(f"3. Detected language: {metadata.language}")

    if metadata.language == "en":
        print(f"   Translating {len(pages)} page(s) to Arabic via Ollama (this is the slow step)...")
        pages = translate_pages(pages, manual_name=PDF_PATH.name)
        metadata.translated_path = save_translated_manual(pages, PDF_PATH.name)
        metadata.is_translated = True
        print(f"   Done. Saved translated pages to {metadata.translated_path}")
        print(f"   Sample (page {pages[0].page_number}): {pages[0].text[:200]!r}\n")
    else:
        metadata.is_translated = False
        metadata.translated_path = None
        print()

    print("4. Chunking...")
    chunks = chunk_manual(pages, metadata)
    save_chunks(chunks, manual_name=metadata.file_path)
    print(f"   Produced {len(chunks)} chunk(s).")
    if chunks:
        print(f"   Sample chunk[0]: page={chunks[0].page_number} section={chunks[0].section!r}")
        print(f"     text={chunks[0].text[:200]!r}\n")

    print("5. Embedding + storing in Chroma + Postgres...")
    summary = store_manual_chunks(metadata, chunks)
    print(f"   skipped={summary.skipped} reason={summary.reason}")
    print(f"   vehicle_id={summary.vehicle_id} manual_id={summary.manual_id} chunk_count={summary.chunk_count}\n")

    if summary.skipped:
        print("Manual already existed (checksum match) -- nothing new was written; skipping cleanup.")
        return

    print("6. Cleaning up: removing this smoke-test manual so it doesn't block a future full run")
    print("   (dedup is keyed by file checksum, so a stale partial ingestion would make")
    print("   run_ingestion.py silently skip the real full-manual run later).")
    db = SessionLocal()
    try:
        manual_row = db.query(Manual).filter(Manual.id == summary.manual_id).first()
        chunk_ids = [c.chroma_vector_id for c in manual_row.chunks if c.chroma_vector_id]
        if chunk_ids:
            _get_client().get_or_create_collection(name=os.getenv("CHROMA_COLLECTION_NAME", "vehicle_manuals_ar")).delete(ids=chunk_ids)
        db.delete(manual_row)  # cascades to manual_chunks
        db.commit()
        print(f"   Deleted manual row + {len(chunk_ids)} Chroma vector(s). Vehicle row left in place (reused by future runs).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
