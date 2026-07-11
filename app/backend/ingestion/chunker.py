"""
app/backend/ingestion/chunker.py

Splits each page's text into overlapping, page-aware chunks and attaches
manual-level metadata (manual_name, make, model, year, language) plus a
best-effort section guess to every chunk.

Chunking never crosses a page boundary: a chunk's `page_number` must
always exactly match a real page in the source manual, since citations
depend on it. This means the last chunk of a page can be shorter than
the target chunk size -- that's preferred over merging text across pages
and losing page-accurate citations.

IMPORTANT: chunk the *Arabic* pages. For a manual that was translated,
that means the pages produced by ingestion.translator.translate_pages,
not the original English pdf_parser output -- see
ingestion.manual_processor.process_manual, which returns exactly the
right page list to pass in here.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from ingestion.pdf_parser import PageText
from api.schemas import ManualMetadata

logger = logging.getLogger("chunker")

DEFAULT_CHUNK_SIZE_WORDS = 220     # a few paragraphs: small enough for embedding + LLM context
DEFAULT_CHUNK_OVERLAP_WORDS = 40   # ~18% overlap, enough to avoid losing context at chunk boundaries
MIN_CHUNK_WORDS = 15               # a trailing chunk shorter than this is merged into the previous one


@dataclass
class Chunk:
    chunk_index: int
    page_number: int
    text: str

    # manual-level metadata, repeated on every chunk so retrieval filters
    # (and citations) never need a join back to the manual record
    manual_name: str
    make: str
    model: str
    year: Optional[str]
    language: str
    section: Optional[str] = None


def _guess_section(page_text: str) -> Optional[str]:
    """
    Best-effort section title: the first line of the page, if it looks
    like a heading (short, no trailing sentence punctuation).

    Manuals don't carry structured heading metadata at this stage, so
    this is a heuristic, not a guarantee -- callers must treat `section`
    as optional (it is frequently None).
    """
    stripped = page_text.strip()
    if not stripped:
        return None

    first_line = stripped.splitlines()[0].strip()
    if 0 < len(first_line) <= 80 and not first_line.endswith((".", "،", "؟", "!", ":")):
        return first_line
    return None


def _word_spans_with_overlap(total_words: int, chunk_size: int, overlap: int) -> list[tuple[int, int]]:
    """
    Compute (start, end) index spans over `total_words`, each `chunk_size`
    words wide, stepping forward by (chunk_size - overlap) so consecutive
    spans share `overlap` words.
    """
    if total_words == 0:
        return []

    step = max(chunk_size - overlap, 1)
    spans: list[tuple[int, int]] = []
    start = 0
    while start < total_words:
        end = min(start + chunk_size, total_words)
        spans.append((start, end))
        if end >= total_words:
            break
        start += step

    # Merge a too-short trailing span into the previous one rather than
    # emitting a near-empty final chunk.
    if len(spans) > 1:
        last_start, last_end = spans[-1]
        if last_end - last_start < MIN_CHUNK_WORDS:
            spans.pop()
            prev_start, _ = spans[-1]
            spans[-1] = (prev_start, last_end)

    return spans


def chunk_page(
    page: PageText,
    manual: ManualMetadata,
    start_index: int,
    chunk_size: int = DEFAULT_CHUNK_SIZE_WORDS,
    overlap: int = DEFAULT_CHUNK_OVERLAP_WORDS,
) -> list[Chunk]:
    """Chunk a single page's text, tagging every chunk with `page.page_number`."""
    words = page.text.split()
    if not words:
        return []

    section = _guess_section(page.text)
    manual_name = Path(manual.file_path).name

    chunks: list[Chunk] = []
    for offset, (start, end) in enumerate(_word_spans_with_overlap(len(words), chunk_size, overlap)):
        chunks.append(
            Chunk(
                chunk_index=start_index + offset,
                page_number=page.page_number,
                text=" ".join(words[start:end]),
                manual_name=manual_name,
                make=manual.make,
                model=manual.model,
                year=manual.year,
                language=manual.language,
                section=section,
            )
        )
    return chunks


def chunk_manual(
    pages: list[PageText],
    manual: ManualMetadata,
    chunk_size: int = DEFAULT_CHUNK_SIZE_WORDS,
    overlap: int = DEFAULT_CHUNK_OVERLAP_WORDS,
) -> list[Chunk]:
    """
    Chunk every page of a manual, preserving global chunk ordering via a
    continuously-incrementing `chunk_index` across pages.

    Empty pages (no usable text even after OCR) simply produce no chunks.
    """
    all_chunks: list[Chunk] = []
    for page in pages:
        page_chunks = chunk_page(
            page, manual, start_index=len(all_chunks), chunk_size=chunk_size, overlap=overlap
        )
        all_chunks.extend(page_chunks)

    logger.info(
        "Chunked %s: %d page(s) -> %d chunk(s)",
        Path(manual.file_path).name, len(pages), len(all_chunks),
    )
    return all_chunks


def save_chunks(
    chunks: list[Chunk],
    manual_name: str,
    output_dir: str | Path = "data/processed_chunks",
) -> str | None:
    """
    Persist chunks to data/processed_chunks/<manual_name>.chunks.json
    *before* embedding, so chunking and embedding can be re-run/retried
    independently. Returns the path written to, or None on failure
    (ingestion continues either way -- the caller still has the chunks
    in memory).
    """
    output_dir = Path(output_dir)

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(manual_name).stem
        output_path = output_dir / f"{stem}.chunks.json"

        payload = [asdict(c) for c in chunks]
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("Saved %d processed chunk(s) to %s", len(chunks), output_path)
        return str(output_path)
    except Exception as exc:
        logger.error("Failed to save processed chunks for %s: %s", manual_name, exc)
        return None
