"""
app/backend/ingestion/manual_processor.py

Orchestrates the per-manual ingestion steps covered by this batch of
tickets, in order:

    1. PDF text extraction (pdf_parser.py), with OCR fallback for
       weak/scanned pages (ocr_fallback.py)
    2. Language detection (language_detector.py)
    3. Translation into Arabic for English manuals only (translator.py)

Chunking, embedding, and storage in Chroma/Postgres are separate, later
pipeline stages (see README roadmap) and are intentionally not done here.
"""

from __future__ import annotations

import logging
from pathlib import Path

from ingestion.language_detector import detect_manual_language
from ingestion.pdf_parser import PageText, extract_pdf_pages
from ingestion.translator import save_translated_manual, translate_pages
from app.backend.api.schemas import ManualMetadata

logger = logging.getLogger("manual_processor")


def process_manual(metadata: ManualMetadata) -> tuple[ManualMetadata, list[PageText]]:
    """
    Run extraction -> language detection -> translation for one manual,
    filling in the ingestion-stage fields on `metadata` in place.

    Returns a (metadata, pages) tuple where `pages` is always the
    **Arabic** page list -- the translated pages for an English manual,
    or the original pages if the manual was already Arabic. Downstream
    chunking (ingestion.chunker) must chunk `pages`, never the raw
    pdf_parser output, since the corpus language is locked to Arabic.
    """
    pdf_path = Path(metadata.file_path)

    extraction = extract_pdf_pages(pdf_path)
    metadata.total_pages = extraction.total_pages
    metadata.ocr_page_count = extraction.ocr_page_count
    metadata.extraction_errors = extraction.errors

    metadata.language = detect_manual_language(page.text for page in extraction.pages)

    if metadata.language == "en":
        logger.info("Translating %s from English to Arabic", pdf_path.name)
        translated_pages = translate_pages(extraction.pages, manual_name=pdf_path.name)
        metadata.translated_path = save_translated_manual(translated_pages, pdf_path.name)
        metadata.is_translated = True
        arabic_pages = translated_pages
    else:
        metadata.is_translated = False
        metadata.translated_path = None
        arabic_pages = extraction.pages

    logger.info(
        "Processed %s: language=%s pages=%s ocr_pages=%d translated=%s",
        pdf_path.name,
        metadata.language,
        metadata.total_pages,
        metadata.ocr_page_count,
        metadata.is_translated,
    )
    return metadata, arabic_pages