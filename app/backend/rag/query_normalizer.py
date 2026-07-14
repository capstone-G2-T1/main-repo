"""Conservative Arabic and mixed-language query normalization."""

from __future__ import annotations

import re
import unicodedata

_ARABIC_DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
_TATWEEL = "\u0640"
_WHITESPACE = re.compile(r"\s+")


def normalize_query(question: str) -> str:
    """Normalize only safe Unicode/Arabic presentation differences."""
    if not question or not question.strip():
        raise ValueError("السؤال لا يمكن أن يكون فارغا")
    text = unicodedata.normalize("NFKC", question.strip())
    text = text.replace(_TATWEEL, "")
    text = _ARABIC_DIACRITICS.sub("", text)
    return _WHITESPACE.sub(" ", text).strip()
