"""
app/backend/ingestion/language_detector.py

Detects whether a manual's extracted text is Arabic or English, which
determines whether the manual needs to go through translation before it
joins the (locked) Arabic corpus.

A lightweight, dependency-free character-ratio heuristic is used instead
of a statistical language-ID model, matching the rest of the query/NER
layer, which is deliberately rule-based (no model training required).

Detection never raises. If the text is missing, too short, or otherwise
inconclusive, the result defaults to "en" -- routing an already-Arabic
manual through translation is a wasted (but harmless) step, whereas
mis-defaulting an English manual to "ar" would let untranslated English
text leak into the Arabic corpus.
"""

from __future__ import annotations

import logging
import re
from typing import Iterable

logger = logging.getLogger("language_detector")

_ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")
_LATIN_RE = re.compile(r"[A-Za-z]")

DEFAULT_LANGUAGE = "en"
_MIN_ALPHA_CHARS = 20          # below this, detection is unreliable -> default
_ARABIC_RATIO_THRESHOLD = 0.5  # majority-Arabic characters -> "ar"


def detect_language(text: str | None) -> str:
    """
    Detect whether `text` is Arabic ("ar") or English ("en").

    Defaults to "en" whenever the text is missing or too short to be
    confident about.
    """
    if not text or not text.strip():
        return DEFAULT_LANGUAGE

    arabic_chars = len(_ARABIC_RE.findall(text))
    latin_chars = len(_LATIN_RE.findall(text))
    total_alpha = arabic_chars + latin_chars

    if total_alpha < _MIN_ALPHA_CHARS:
        return DEFAULT_LANGUAGE

    arabic_ratio = arabic_chars / total_alpha
    return "ar" if arabic_ratio >= _ARABIC_RATIO_THRESHOLD else DEFAULT_LANGUAGE


def detect_manual_language(page_texts: Iterable[str], sample_pages: int = 5) -> str:
    """
    Detect the dominant language of a manual from a sample of its pages.

    Sampling (rather than scanning the whole manual) keeps detection fast
    on large manuals while staying robust to a handful of blank or
    image-only pages at the start of a PDF (covers, tables of contents).
    """
    sample: list[str] = []
    for text in page_texts:
        if text and text.strip():
            sample.append(text)
        if len(sample) >= sample_pages:
            break

    if not sample:
        logger.warning(
            "No usable text found for language detection; defaulting to '%s'",
            DEFAULT_LANGUAGE,
        )
        return DEFAULT_LANGUAGE

    language = detect_language("\n".join(sample))
    logger.info("Detected manual language: %s (sampled %d page(s))", language, len(sample))
    return language
