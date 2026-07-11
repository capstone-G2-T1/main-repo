"""Normalize Arabic and mixed-language questions before retrieval."""

from __future__ import annotations

import re

_TASHKEEL = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
_LETTER_TRANSLATION = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه"})

_ENGLISH_TERMS = {
    "regenerative braking": "الفرمله التجديديه",
    "heat pump": "مضخه الحراره",
    "battery": "البطاريه",
    "charging": "الشحن",
    "charge": "الشحن",
    "range": "مدي القياده",
    "motor": "المحرك الكهربائي",
    "inverter": "المحول الكهربائي",
    "bms": "نظام اداره البطاريه",
    "obc": "شاحن السياره المدمج",
    "torque": "عزم الدوران",
    "autopilot": "القياده الذاتيه",
}

_DIALECT_TERMS = {
    "شو": "ما",
    "وين": "اين",
    "بلاقي": "اجد",
    "كفرات": "اطارات",
    "كوشوك": "اطارات",
    "موتور": "محرك",
    "لمبه": "مصباح",
    "شاشه": "شاشه العرض",
    "مكيف": "تكييف الهواء",
    "فرامل": "مكابح",
}


def _replace_terms(text: str, replacements: dict[str, str], ignore_case: bool = False) -> str:
    for term in sorted(replacements, key=len, reverse=True):
        flags = re.IGNORECASE if ignore_case else 0
        text = re.sub(re.escape(term), replacements[term], text, flags=flags)
    return text


def normalize_query(question: str) -> str:
    """Return a stable Arabic search form while preserving vehicle names and codes."""
    if not question or not question.strip():
        raise ValueError("السؤال لا يمكن أن يكون فارغاً")
    text = _TASHKEEL.sub("", question.strip())
    text = text.translate(_LETTER_TRANSLATION)
    text = _replace_terms(text, _ENGLISH_TERMS, ignore_case=True)
    text = _replace_terms(text, _DIALECT_TERMS)
    return " ".join(text.split())
