import pytest

from rag.intent_classifier import classify_intent


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("لمبة ABS ولعت", "warning_light"),
        ("what does this warning light mean", "warning_light"),
        ("متى أغير الزيت؟", "maintenance"),
        ("maintenance interval", "maintenance"),
        ("السيارة لا تشحن", "troubleshooting"),
        ("the screen is not working", "troubleshooting"),
        ("كيف أغير اللغة؟", "settings"),
        ("how to enable bluetooth", "settings"),
        ("هل يمكن تعطيل الإيرباق؟", "safety"),
        ("child seat safety", "safety"),
        ("كم سعة البطارية؟", "specification"),
        ("what is the tire pressure", "specification"),
        ("وين ألاقي معلومات بالكتيب؟", "general_manual_question"),
        ("tell me about this vehicle", "general_manual_question"),
    ],
)
def test_intents(question, expected):
    assert classify_intent(question) == expected


def test_empty_falls_back():
    assert classify_intent("") == "general_manual_question"
