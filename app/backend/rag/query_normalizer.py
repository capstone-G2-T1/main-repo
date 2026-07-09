"""
query_normalizer.py
-------------------
Normalizes Arabic user questions before retrieval.

Pipeline (in order):
    1. Remove tashkeel (diacritics)
    2. Normalize Arabic letter variants (أ/إ/آ → ا, ى → ي, ة → ه)
    3. Replace mixed English/Arabic EV terms with Arabic equivalents
    4. Replace dialect terms with Modern Standard Arabic equivalents
    5. Strip extra whitespace
"""
import re
import unicodedata


_TASHKEEL = re.compile(
    r"[\u0610-\u061A"   # Arabic extended
    r"\u064B-\u065F"    # Fathah, dammah, kasrah, tanween, shadda, sukun …
    r"\u0670"           # Superscript alef
    r"\u06D6-\u06DC"    # Small high ligatures
    r"\u06DF-\u06E4"    # More small marks
    r"\u06E7\u06E8"
    r"\u06EA-\u06ED]"   # More Arabic marks
)

_LETTER_MAP: dict[str, str] = {
    "أ": "ا",
    "إ": "ا",
    "آ": "ا",
    "ى": "ي",
    "ة": "ه",   # optional — keeps matching stable
    "\u0671": "ا",  # wasla alef
}

_EN_TO_AR: dict[str, str] = {
    "battery":              "البطارية",
    "charging":             "الشحن",
    "charge":               "الشحن",
    "range":                "مدى القيادة",
    "motor":                "المحرك الكهربائي",
    "regenerative braking": "الفرملة التجديدية",
    "regenerative":         "التجديدية",
    "inverter":             "المحول الكهربائي",
    "bms":                  "نظام ادارة البطارية",
    "tpms":                 "نظام مراقبة ضغط الاطارات",
    "obc":                  "شاحن السيارة المدمج",
    "heat pump":            "مضخة الحرارة",
    "torque":               "عزم الدوران",
    "kilowatt":             "كيلوواط",
    "kw":                   "كيلوواط",
    "autopilot":            "القيادة الذاتية",
    "regeneration":         "استعادة الطاقة",
    "soc":                  "مستوى شحن البطارية",
}

_DIALECT_TO_MSA: dict[str, str] = {
    "كفرات":          "اطارات",
    "شحن السياره":    "شحن البطارية",
    "شحن السيارة":    "شحن البطارية",
    "موتور":          "المحرك الكهربائي",
    "بطارية فاضيه":   "البطارية منخفضة الشحن",
    "بطارية فاضية":   "البطارية منخفضة الشحن",
    "لمبة حمرا":      "مصباح تحذير",
    "لمبه حمرا":      "مصباح تحذير",
    "ريموت":          "جهاز التحكم عن بعد",
    "شاشه":           "شاشة العرض",
    "شاشة":           "شاشة العرض",
    "مكيف":           "تكييف الهواء",
    "بلاقة":          "موصل الشحن",
    "كابل الشحن":     "سلك الشحن",
    "جنط":            "الجنط",
    "فرامل":          "مكابح",
    "بلد":            "مدى القيادة المتبقي",
    "طاقه":           "مستوى الشحن",
    "طاقة":           "مستوى الشحن",
    "سرعة الشحن":     "معدل الشحن",
    "سرعه الشحن":     "معدل الشحن",
}




def _remove_tashkeel(text: str) -> str:
    return _TASHKEEL.sub("", text)


def _normalize_letters(text: str) -> str:
    for original, replacement in _LETTER_MAP.items():
        text = text.replace(original, replacement)
    return text


def _replace_english_terms(text: str) -> str:
    """
    Replaces English EV terms (case-insensitive) inside Arabic sentences.
    Longer phrases are matched before shorter words to avoid partial replacement.
    """
    sorted_terms = sorted(_EN_TO_AR.keys(), key=len, reverse=True)
    for term in sorted_terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        text = pattern.sub(_EN_TO_AR[term], text)
    return text


def _replace_dialect_terms(text: str) -> str:
    """
    Replaces dialect words/phrases with MSA equivalents.
    Longer phrases are matched first.
    """
    sorted_terms = sorted(_DIALECT_TO_MSA.keys(), key=len, reverse=True)
    for term in sorted_terms:
        text = text.replace(term, _DIALECT_TO_MSA[term])
    return text


def _clean_whitespace(text: str) -> str:
    return " ".join(text.split())




def normalize_query(question: str) -> str:
    """
    Normalizes an Arabic user question before retrieval.

    Steps:
        1. Remove tashkeel
        2. Normalize letter variants
        3. Replace English EV terms with Arabic
        4. Replace dialect terms with MSA
        5. Clean whitespace

    Args:
        question: Raw Arabic question from the user.

    Returns:
        Normalized Arabic question ready for embedding and retrieval.

    Raises:
        ValueError: If the question is empty or whitespace-only.
    """
    if not question or not question.strip():
        raise ValueError("السؤال لا يمكن أن يكون فارغاً")

    text = question.strip()
    text = _remove_tashkeel(text)
    text = _normalize_letters(text)
    text = _replace_english_terms(text)
    text = _replace_dialect_terms(text)
    text = _clean_whitespace(text)

    return text