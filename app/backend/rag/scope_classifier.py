"""Deterministic scope classification before retrieval."""

from __future__ import annotations

import re
from typing import Literal

Scope = Literal["in_scope", "out_of_scope", "uncertain"]

_OUT_OF_SCOPE_PATTERNS = (
    r"\b(price|prices|cost|msrp|fuel price|gas price|weather|forecast|rain|sports|football|basketball|news)\b",
    r"\b(program|code|python|javascript|sql|api|website|app|cooking|recipe)\b",
    r"\b(book|appointment|nearest|near me|location|service center|dealer|dealership|rating|ratings|review|reviews)\b",
    r"(سعر|أسعار|اسعار|تكلفة|الطقس|توقعات|رياض|مباراة|اخبار|أخبار|برمج|بايثون|جافاسكربت|احجز|موعد|اقرب|أقرب|موقعي|مركز صيانة|وكالة|تقييم)",
)

_IN_SCOPE_PATTERNS = (
    r"\b(warning|light|maintenance|troubleshoot|setting|safety|specification|charge|charging|tire|tyre|brake|battery|airbag|fuse|climate|abs|tpms|epb|ready|manual|owner|[pbcu][0-9a-f]{4})\b",
    r"(لمبة|تحذير|صيانة|عطل|مشكلة|إعداد|اعداد|سلامة|مواصفات|شحن|إطار|اطار|فرامل|مكابح|بطارية|وسادة|ايرباق|فيوز|مكيف|تكييف|دليل|كتيب)",
)


def classify_scope(question: str) -> Scope:
    """Classify whether a question can be answered from an owner manual."""
    text = " ".join((question or "").casefold().split())
    if not text:
        return "uncertain"
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in _OUT_OF_SCOPE_PATTERNS):
        if not any(re.search(pattern, text, re.IGNORECASE) for pattern in _IN_SCOPE_PATTERNS):
            return "out_of_scope"
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in _IN_SCOPE_PATTERNS):
        return "in_scope"
    return "uncertain"
