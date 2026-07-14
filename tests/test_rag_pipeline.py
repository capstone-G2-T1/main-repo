from rag import pipeline
from rag.types import RetrievedChunk


def test_pipeline_connects_all_stages(monkeypatch):
    candidate = RetrievedChunk("1", "نص موثوق", {"manual_name": "VW_ID4", "page": 7}, retrieval_score=0.8)
    captured = {}

    def fake_retrieve(original, normalized, where, top_k=None):
        captured["original"] = original
        captured["normalized"] = normalized
        captured["where"] = where
        captured["top_k"] = top_k
        return [candidate], {
            "original_candidate_count": 1,
            "normalized_candidate_count": 0,
            "merged_candidate_count": 1,
        }

    monkeypatch.setattr(pipeline, "retrieve_fused_chunks", fake_retrieve)
    monkeypatch.setattr(pipeline, "rerank_chunks", lambda query, chunks, top_k=None: chunks[: top_k or 5])
    monkeypatch.setattr(
        pipeline,
        "generate_answer",
        lambda *args: ("جواب موثوق\n\nالمصدر: VW_ID4، الصفحة 7.", [{"manual_name": "VW_ID4", "page": 7, "section": None}]),
    )

    result = pipeline.run_rag_pipeline("لمبة ABS في VW ID4", "VW ID4")
    assert result.intent == "warning_light"
    assert result.entities["model"] == "ID.4"
    assert captured["where"]["$and"][0] == {"make": {"$in": ["Volkswagen", "VW", "Vw"]}}
    assert captured["where"]["$and"][1] == {"model": {"$in": ["ID.4", "ID4"]}}
    assert captured["top_k"] >= 15
    assert result.citations[0]["page"] == 7
    assert result.retrieved_chunks[0]["id"] == "1"
    assert result.scope == "in_scope"


def test_out_of_scope_skips_retrieval(monkeypatch):
    def fail_retrieve(*args, **kwargs):
        raise AssertionError("retrieval should not run")

    monkeypatch.setattr(pipeline, "retrieve_fused_chunks", fail_retrieve)
    result = pipeline.run_rag_pipeline("What is the current price of this car?", "VW ID4")
    assert result.refused is True
    assert result.scope == "out_of_scope"
    assert result.citations == []


def test_pipeline_insufficient_evidence_has_no_citations(monkeypatch):
    weak = RetrievedChunk("1", "weak", {"manual_name": "VW_ID4", "page": 7}, retrieval_score=0.001)
    monkeypatch.setattr(
        pipeline,
        "retrieve_fused_chunks",
        lambda *args, **kwargs: (
            [weak],
            {"original_candidate_count": 1, "normalized_candidate_count": 0, "merged_candidate_count": 1},
        ),
    )
    monkeypatch.setattr(pipeline, "rerank_chunks", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError()))
    result = pipeline.run_rag_pipeline("سؤال غامض عن الدليل", "VW ID4")
    assert result.insufficient_evidence is True
    assert result.refused is False
    assert result.citations == []
