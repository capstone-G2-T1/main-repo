from rag.generator import NO_CONTEXT_REFUSAL, generate_answer
from rag.types import ExtractedEntities, RetrievedChunk


def chunk(page=42):
    return RetrievedChunk(
        "1",
        "افحص نظام شحن البطارية.",
        {"manual_name": "BYD Dolphin.pdf", "page": page, "section": "Warnings"},
    )


def test_no_context_refuses_without_calling_ollama():
    answer, citations = generate_answer(
        "سؤال",
        "سؤال",
        ExtractedEntities(),
        "general_manual_question",
        None,
        [],
        post_json=lambda *_: (_ for _ in ()).throw(AssertionError()),
    )
    assert answer == NO_CONTEXT_REFUSAL
    assert citations == []


def test_grounded_answer_uses_only_real_citation():
    answer, citations = generate_answer(
        "شو يعني الضوء؟",
        "ما يعني الضوء؟",
        ExtractedEntities(make="BYD"),
        "warning_light",
        "BYD Dolphin",
        [chunk()],
        post_json=lambda *_: {"response": "يشير الضوء إلى مشكلة في نظام الشحن.\nالمصدر: fake.pdf page 999"},
    )
    assert "page 999" not in answer
    assert "الصفحة 42" in answer
    assert citations == [{"manual_name": "BYD Dolphin", "page": 42, "section": "Warnings"}]


def test_ollama_failure_is_safe():
    answer, citations = generate_answer(
        "q",
        "q",
        ExtractedEntities(),
        "general_manual_question",
        None,
        [chunk()],
        post_json=lambda *_: (_ for _ in ()).throw(ConnectionError()),
    )
    assert (answer, citations) == (NO_CONTEXT_REFUSAL, [])
