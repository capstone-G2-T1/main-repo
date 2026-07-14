"""Rule-based intent classification for Arabic and English manual questions."""

from __future__ import annotations

import re

from rag.query_normalizer import normalize_query


INTENTS = {
    "warning_light",
    "maintenance",
    "troubleshooting",
    "settings",
    "safety",
    "specification",
    "general_manual_question",
}

# Priority resolves overlaps deterministically: explicit warnings beat generic
# failures, while safety instructions beat a generic "how" settings phrase.
RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("warning_light", (r"تحذير", r"لمب[هة]", r"مصباح", r"اشار[هة]", r"warning", r"warning light", r"\b(?:ABS|EPB|ESC|SRS|TPMS)\b", r"\b[PBCU][0-9A-F]{4}\b")),
    ("maintenance", (r"صيان[هة]", r"جدول الصيان", r"مت[ىي].*(?:اغير|أغير|تغيير|استبدال|تبديل)", r"كل كم", r"service interval", r"maintenance", r"replace.*(?:filter|oil)")),
    ("safety", (r"سلام[هة]", r"احتياط", r"مقعد الطفل", r"طوارئ", r"سحب السيار", r"تعطيل.*(?:ايرباق|إيرباق|وساد)", r"safety", r"child seat", r"emergency", r"towing")),
    ("troubleshooting", (r"لا (?:يعمل|تعمل|يشتغل|تشتغل|يفتح|تبرد|يشحن|تشحن)", r"ما (?:بشتغل|بتشتغل|يفتح)", r"مشكل[هة]", r"عطل", r"كيف احل", r"not working", r"won't", r"does not work", r"problem")),
    ("settings", (r"كيف (?:اغير|أغير|افعل|أفعل|اضبط|أضبط|اشغل|أشغل|اعد|أعد)", r"اعدادات|إعدادات", r"بلوتوث", r"اللغه|اللغة", r"الساع[هة]", r"configure", r"enable", r"change.*setting", r"pair.*bluetooth")),
    ("specification", (r"كم", r"سع[هة]", r"ضغط", r"ابعاد", r"مقاس", r"مدى السيار", r"نوع الزيت", r"capacity", r"dimension", r"pressure", r"size", r"range", r"specification")),
)


def classify_intent(question: str) -> str:
    """Return exactly one supported intent, falling back safely for unclear input."""
    if not question or not question.strip():
        return "general_manual_question"
    try:
        text = normalize_query(question)
    except ValueError:
        return "general_manual_question"

    for intent, patterns in RULES:
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns):
            return intent
    return "general_manual_question"
