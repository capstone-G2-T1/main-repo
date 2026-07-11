from api.schemas import RagResult
from rag import pipeline
from rag.generator import NO_CONTEXT_REFUSAL
from rag.types import RetrievedChunk


def test_pipeline_connects_all_stages(monkeypatch):
    candidate = RetrievedChunk("1", "نص موثوق", {"manual_name": "manual.pdf", "page": 7})
    captured = {}

    def fake_retrieve(query, where):
        captured["query"] = query
        captured["where"] = where
        return [candidate]

    monkeypatch.setattr(pipeline, "retrieve_chunks", fake_retrieve)
    monkeypatch.setattr(pipeline, "rerank_chunks", lambda query, chunks: chunks)
    monkeypatch.setattr(
        pipeline,
        "generate_answer",
        lambda *args: ("جواب موثوق\n\nالمصدر: manual.pdf، الصفحة 7.", [{"manual_name": "manual.pdf", "page": 7, "section": None}]),
    )

    result = pipeline.run_rag_pipeline("لمبة ABS في BYD Dolphin 2024", "BYD Dolphin 2024")
    assert result.intent == "warning_light"
    assert result.entities["model"] == "Dolphin"
    assert captured["where"]["$and"][2] == {"year": {"$eq": "2024"}}
    assert result.citations[0]["page"] == 7
    assert result.retrieved_chunks[0]["id"] == "1"


def test_pipeline_no_results_refuses(monkeypatch):
    monkeypatch.setattr(pipeline, "retrieve_chunks", lambda *_: [])
    monkeypatch.setattr(pipeline, "rerank_chunks", lambda *_: [])
    monkeypatch.setattr(pipeline, "generate_answer", lambda *args: (NO_CONTEXT_REFUSAL, []))
    result = pipeline.run_rag_pipeline("سؤال غير موجود")
    assert result.answer == NO_CONTEXT_REFUSAL
    assert result.confidence == "low"
    assert result.citations == []
