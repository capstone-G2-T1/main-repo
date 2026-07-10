"""
app/backend/ingestion/translator.py

Translates English manual text into Arabic during ingestion, reusing the
same local Ollama model already running in the stack (qwen2.5:7b-instruct)
instead of adding a separate translation dependency/model download.

IMPORTANT: this module is only ever imported by the ingestion pipeline
(ingestion/manual_processor.py). The RAG runtime (app/backend/rag/*,
served by /ask) never imports it, so no translation can happen at query
time -- translation is strictly an ingestion-time step.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import requests

from ingestion.pdf_parser import PageText

logger = logging.getLogger("translator")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
REQUEST_TIMEOUT_SECONDS = 120

_TRANSLATION_PROMPT = (
    "Translate the following vehicle manual text from English into Modern "
    "Standard Arabic. Preserve technical terms, part names, and warning "
    "labels precisely. Return ONLY the Arabic translation, with no preamble, "
    "no notes, and no English.\n\n"
    "Text:\n{text}"
)


class TranslationError(RuntimeError):
    """Raised when the local translation model is unreachable or returns nothing usable."""


def translate_text(text: str) -> str:
    """
    Translate a single page (or chunk) of English text into Arabic via Ollama.

    Empty input returns empty output without calling the model.
    """
    if not text or not text.strip():
        return ""

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": _TRANSLATION_PROMPT.format(text=text),
                "stream": False,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        translated = response.json().get("response", "").strip()
    except Exception as exc:
        raise TranslationError(f"Ollama translation request failed: {exc}") from exc

    if not translated:
        raise TranslationError("Ollama returned an empty translation")

    return translated


def translate_pages(pages: list[PageText], manual_name: str = "") -> list[PageText]:
    """
    Translate every page's text from English to Arabic, preserving page numbers.

    A page that fails to translate keeps its original English text (and is
    logged) rather than aborting translation for the whole manual.
    """
    translated_pages: list[PageText] = []

    for page in pages:
        if not page.text.strip():
            translated_pages.append(page)
            continue

        try:
            arabic_text = translate_text(page.text)
            translated_pages.append(
                PageText(
                    page_number=page.page_number,
                    text=arabic_text,
                    used_ocr=page.used_ocr,
                    is_empty=page.is_empty,
                )
            )
        except TranslationError as exc:
            logger.error(
                "%s page %d: translation failed, keeping original text: %s",
                manual_name or "manual",
                page.page_number,
                exc,
            )
            translated_pages.append(page)

    return translated_pages


def save_translated_manual(
    pages: list[PageText],
    manual_name: str,
    output_dir: str | Path = "data/translated_manuals",
) -> str | None:
    """
    Persist translated pages to data/translated_manuals/<manual_name>.ar.json.

    Stored as page-aware JSON rather than a re-rendered PDF, so page
    numbers stay exactly aligned with `chunk_text` for chunking and
    citations downstream. Returns the path written to, or None if saving
    failed -- the caller still has the translated pages in memory either
    way, so a save failure doesn't need to abort ingestion.
    """
    output_dir = Path(output_dir)

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(manual_name).stem
        output_path = output_dir / f"{stem}.ar.json"

        payload = [{"page_number": p.page_number, "text": p.text} for p in pages]
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("Saved translated manual to %s", output_path)
        return str(output_path)
    except Exception as exc:
        logger.error("Failed to save translated manual for %s: %s", manual_name, exc)
        return None
