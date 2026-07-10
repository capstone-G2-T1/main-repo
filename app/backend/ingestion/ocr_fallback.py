"""
app/backend/ingestion/ocr_fallback.py

OCR fallback for scanned/image-only PDF pages, or pages where
pdfplumber's text layer is missing or too weak to be usable.

Only pages flagged as "weak" (see `needs_ocr`) are rasterized and OCR'd --
running Tesseract on every page would be slow and unnecessary for the
(common) case of a manual that already has a clean text layer.
"""

from __future__ import annotations

import logging

import pytesseract

logger = logging.getLogger("ocr_fallback")

# Both language packs, since manuals may mix Arabic UI labels with
# English part numbers / error codes on the same scanned page.
OCR_LANGUAGES = "ara+eng"
OCR_RESOLUTION = 300
MIN_TEXT_CHARS = 20  # pages with fewer non-whitespace chars than this are "weak"


def needs_ocr(text: str | None) -> bool:
    """Return True if pdfplumber's extracted text for a page is missing or too weak to trust."""
    return not text or len(text.strip()) < MIN_TEXT_CHARS


def ocr_page(page, page_number: int, manual_name: str = "") -> str:
    """
    Run Tesseract OCR on a single pdfplumber page.

    Returns an empty string (rather than raising) on failure, so one
    unreadable page never aborts ingestion for the rest of the manual --
    the caller logs/counts the outcome at the page level.
    """
    try:
        image = page.to_image(resolution=OCR_RESOLUTION).original
        text = pytesseract.image_to_string(image, lang=OCR_LANGUAGES)
        return text.strip()
    except Exception as exc:  # noqa: BLE001 - rendering/OCR can fail in many ways; never stop ingestion
        logger.error(
            "OCR failed for %s page %d: %s", manual_name or "manual", page_number, exc
        )
        return ""
