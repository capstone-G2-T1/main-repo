"""
app/backend/ingestion/pdf_parser.py

Extracts text from every page of a manual PDF using pdfplumber, falling
back to Tesseract OCR (ingestion.ocr_fallback) for pages whose text
layer is missing or too weak (scanned pages, image-only pages, etc.).

Page numbers are preserved throughout so downstream chunking/citation
can always point back to an exact page in the source manual.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber

from ingestion.ocr_fallback import needs_ocr, ocr_page

logger = logging.getLogger("pdf_parser")


@dataclass
class PageText:
    """Extracted text for a single page, plus how it was obtained."""

    page_number: int  # 1-indexed, matches the page a user would read in the PDF
    text: str
    used_ocr: bool = False
    is_empty: bool = False  # true if neither pdfplumber nor OCR produced usable text


@dataclass
class ExtractionResult:
    pages: list[PageText] = field(default_factory=list)
    total_pages: int = 0
    ocr_page_count: int = 0
    errors: list[str] = field(default_factory=list)


def extract_pdf_pages(pdf_path: str | Path) -> ExtractionResult:
    """
    Extract text page-by-page from `pdf_path`.

    Behavior:
        - pdfplumber is tried first on every page.
        - Pages with missing/weak text (see ocr_fallback.needs_ocr) are
          marked and re-extracted via OCR fallback automatically.
        - A single page's failure is logged and recorded in `errors`
          (never raised), so the rest of the manual still ingests.

    Returns:
        ExtractionResult with one PageText per page (in page order),
        the total OCR page count, and any per-page errors encountered.
    """
    pdf_path = Path(pdf_path)
    result = ExtractionResult()

    try:
        pdf = pdfplumber.open(pdf_path)
    except Exception as exc:
        msg = f"Failed to open PDF {pdf_path.name}: {exc}"
        logger.error(msg)
        result.errors.append(msg)
        return result

    with pdf:
        result.total_pages = len(pdf.pages)

        for index, page in enumerate(pdf.pages):
            page_number = index + 1
            text = ""

            try:
                text = page.extract_text() or ""
            except Exception as exc:
                msg = f"{pdf_path.name} page {page_number}: pdfplumber extraction failed: {exc}"
                logger.error(msg)
                result.errors.append(msg)

            # Weak/empty pages are marked here and immediately handed to
            # the OCR fallback -- this is the "mark for OCR fallback"
            # step; the fallback itself lives in ocr_fallback.py.
            used_ocr = False
            if needs_ocr(text):
                ocr_text = ocr_page(page, page_number, manual_name=pdf_path.name)
                if ocr_text:
                    text = ocr_text
                    used_ocr = True
                    result.ocr_page_count += 1

            is_empty = not text.strip()
            if is_empty:
                logger.warning(
                    "%s page %d has no usable text after pdfplumber + OCR fallback",
                    pdf_path.name,
                    page_number,
                )

            result.pages.append(
                PageText(
                    page_number=page_number,
                    text=text,
                    used_ocr=used_ocr,
                    is_empty=is_empty,
                )
            )

    logger.info(
        "Extracted %s: %d page(s), %d via OCR, %d error(s)",
        pdf_path.name,
        result.total_pages,
        result.ocr_page_count,
        len(result.errors),
    )
    return result
