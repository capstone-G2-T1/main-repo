"""
Backfills translation for pages of BYD_DOLPHIN_2025.pdf that fell back to their
original English text during the earlier full ingestion run (scripts/run_full_ingestion.py),
because Docker Desktop's engine hung mid-run and the corresponding Ollama calls failed.

Re-extracts and re-translates only FAILED_PAGES, patches the saved translated-manual
JSON, re-chunks just those pages, and replaces the corresponding rows in Postgres
(manual_chunks) and vectors in Chroma -- the 164 pages that translated successfully
the first time are left untouched.

    python scripts/backfill_translations.py
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "app" / "backend"
for path in (str(BACKEND), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

os.environ.setdefault("CHROMA_HOST", "localhost")
os.environ.setdefault("CHROMA_PORT", "8001")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("OLLAMA_HOST", "http://localhost:11434")
os.environ.setdefault("OLLAMA_MODEL", "qwen2.5:7b-instruct")
os.environ["DEBUG"] = "false"

from api.schemas import ManualMetadata  # noqa: E402
from db.models import Manual, ManualChunk  # noqa: E402
from db.session import SessionLocal  # noqa: E402
from ingestion.chunker import chunk_page  # noqa: E402
from ingestion.embedder import embed_texts  # noqa: E402
from ingestion.pdf_parser import PageText, extract_pdf_pages  # noqa: E402
from ingestion.translator import TranslationError, translate_text  # noqa: E402
from ingestion.vector_store import CHROMA_COLLECTION_NAME, _get_client  # noqa: E402

logger = logging.getLogger("backfill_translations")

PDF_PATH = ROOT / "data" / "raw_manuals" / "BYD" / "BYD_DOLPHIN_2025.pdf"
MANUAL_NAME = "BYD_DOLPHIN_2025.pdf"
TRANSLATED_JSON_PATH = ROOT / "data" / "translated_manuals" / "BYD_DOLPHIN_2025.ar.json"
PROCESSED_CHUNKS_PATH = ROOT / "data" / "processed_chunks" / "BYD_DOLPHIN_2025.chunks.json"

# Pages that kept their original English text because translation failed during the
# Docker Desktop outage in the previous full ingestion run.
FAILED_PAGES = {57} | set(range(142, 157)) | set(range(160, 182))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print(f"Backfilling {len(FAILED_PAGES)} page(s): {sorted(FAILED_PAGES)}\n")

    db = SessionLocal()
    manual_row = db.query(Manual).filter(Manual.manual_name == MANUAL_NAME).first()
    if manual_row is None:
        print(f"No Manual row found for {MANUAL_NAME!r} -- run the full ingestion first.")
        db.close()
        return
    manual_id = manual_row.id
    max_chunk_index = max((c.chunk_index for c in manual_row.chunks), default=-1)
    print(f"Manual {manual_id}, current max chunk_index={max_chunk_index}\n")

    print("1. Re-extracting English text for the affected pages...")
    extraction = extract_pdf_pages(PDF_PATH)
    english_pages = {p.page_number: p for p in extraction.pages if p.page_number in FAILED_PAGES}
    print(f"   Extracted {len(english_pages)} of {len(FAILED_PAGES)} target page(s).\n")

    print("2. Re-translating each page individually (Ollama is healthy again)...")
    newly_translated: dict[int, PageText] = {}
    still_failing: list[int] = []
    for page_number in sorted(FAILED_PAGES):
        page = english_pages.get(page_number)
        if page is None or not page.text.strip():
            print(f"   page {page_number}: no source text found, skipping")
            continue
        try:
            arabic_text = translate_text(page.text)
            newly_translated[page_number] = PageText(
                page_number=page_number, text=arabic_text, used_ocr=page.used_ocr, is_empty=False
            )
            print(f"   page {page_number}: OK ({len(arabic_text)} chars)")
        except TranslationError as exc:
            still_failing.append(page_number)
            print(f"   page {page_number}: FAILED again ({exc}); leaving existing chunks untouched")

    print(f"\n   {len(newly_translated)} succeeded, {len(still_failing)} still failing.\n")
    if not newly_translated:
        print("Nothing to backfill.")
        db.close()
        return

    print("3. Patching data/translated_manuals/BYD_DOLPHIN_2025.ar.json...")
    existing_translated = json.loads(TRANSLATED_JSON_PATH.read_text(encoding="utf-8"))
    by_page = {entry["page_number"]: entry["text"] for entry in existing_translated}
    for page_number, page in newly_translated.items():
        by_page[page_number] = page.text
    merged = [{"page_number": n, "text": t} for n, t in sorted(by_page.items())]
    TRANSLATED_JSON_PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"   Patched {len(newly_translated)} page(s) in {TRANSLATED_JSON_PATH}\n")

    print("4. Re-chunking backfilled pages and replacing their rows in Postgres + Chroma...")
    metadata = ManualMetadata(
        make="BYD", model="DOLPHIN", year="2025", file_path=str(PDF_PATH), language="ar"
    )
    next_index = max_chunk_index + 1
    new_chunk_texts: list[str] = []
    new_chunk_rows: list[ManualChunk] = []
    new_vector_ids: list[str] = []
    old_vector_ids: list[str] = []

    for page_number, page in newly_translated.items():
        stale_chunks = [c for c in manual_row.chunks if c.page_number == page_number]
        old_vector_ids.extend(c.chroma_vector_id for c in stale_chunks if c.chroma_vector_id)
        for c in stale_chunks:
            db.delete(c)

        page_chunks = chunk_page(page, metadata, start_index=next_index)
        next_index += len(page_chunks)
        for chunk in page_chunks:
            vector_id = f"{manual_id}:{chunk.chunk_index}"
            new_chunk_texts.append(chunk.text)
            new_vector_ids.append(vector_id)
            new_chunk_rows.append(
                ManualChunk(
                    manual_id=manual_id,
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    section=chunk.section,
                    chunk_text=chunk.text,
                    chroma_vector_id=vector_id,
                )
            )

    if old_vector_ids:
        _get_client().get_or_create_collection(name=CHROMA_COLLECTION_NAME).delete(ids=old_vector_ids)
        print(f"   Deleted {len(old_vector_ids)} stale Chroma vector(s).")

    if new_chunk_texts:
        embeddings = embed_texts(new_chunk_texts)
        metadatas = [
            {
                "make": "BYD", "model": "DOLPHIN", "year": "2025", "page": row.page_number,
                "language": "ar", "manual_name": MANUAL_NAME, "section": row.section or "",
            }
            for row in new_chunk_rows
        ]
        _get_client().get_or_create_collection(name=CHROMA_COLLECTION_NAME).upsert(
            ids=new_vector_ids, embeddings=embeddings, documents=new_chunk_texts, metadatas=metadatas
        )
        print(f"   Upserted {len(new_vector_ids)} new Chroma vector(s).")

    for row in new_chunk_rows:
        db.add(row)
    db.commit()
    # Captured before the session closes below: commit() expires ORM instances by
    # default, so row.chunk_text etc. can't be read again once db.close() detaches them.
    new_chunk_dicts = [
        {
            "chunk_index": row.chunk_index, "page_number": row.page_number, "text": row.chunk_text,
            "manual_name": MANUAL_NAME, "make": "BYD", "model": "DOLPHIN", "year": "2025",
            "language": "ar", "section": row.section,
        }
        for row in new_chunk_rows
    ]
    print(f"   Committed {len(new_chunk_rows)} new manual_chunks row(s) to Postgres.\n")
    db.close()

    print("5. Refreshing data/processed_chunks/BYD_DOLPHIN_2025.chunks.json for consistency...")
    processed = json.loads(PROCESSED_CHUNKS_PATH.read_text(encoding="utf-8"))
    processed = [c for c in processed if c["page_number"] not in newly_translated]
    processed.extend(new_chunk_dicts)
    processed.sort(key=lambda c: c["chunk_index"])
    PROCESSED_CHUNKS_PATH.write_text(json.dumps(processed, ensure_ascii=False, indent=2), encoding="utf-8")
    print("   Done.\n")

    print("=== Backfill summary ===")
    print(f"Re-translated: {sorted(newly_translated.keys())}")
    print(f"New chunks written: {len(new_chunk_rows)}")
    if still_failing:
        print(f"STILL FAILING (left as English, unchanged): {still_failing}")


if __name__ == "__main__":
    main()
