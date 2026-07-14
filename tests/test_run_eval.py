from api.schemas import RagResult
from scripts import run_eval


def _chunk(manual, page):
    return {
        "id": f"{manual}:{page}",
        "text": "x",
        "metadata": {"manual_name": manual, "page": page},
        "retrieval_score": 0.9,
    }


def test_retrieval_metrics_use_manual_and_page_rank():
    question = run_eval.TestQuestion(
        id="q1",
        question="manual question",
        manual="VW_ID4",
        expected_page=5,
    )
    result = RagResult(
        answer="answer",
        citations=[{"manual_name": "VW_ID4", "page": 5}],
        reranked_chunks=[
            _chunk("BYD_SEAGULL", 5),
            _chunk("VW_ID4", 4),
            _chunk("VW_ID4", 5),
            _chunk("GEELY_MK", 5),
            _chunk("VW_ID4", 8),
        ],
    )
    scored = run_eval.score_question(question, result, 12.0, None, 0, "test")
    assert scored.recall_at_3 is True
    assert scored.recall_at_5 is True
    assert scored.mrr == 1 / 3
    assert scored.citation_accuracy is True


def test_recall_at_5_checks_first_five_not_first_three():
    question = run_eval.TestQuestion(id="q1", question="manual question", manual="VW_ID4", expected_page=5)
    result = RagResult(
        answer="answer",
        citations=[],
        reranked_chunks=[
            _chunk("VW_ID4", 1),
            _chunk("VW_ID4", 2),
            _chunk("VW_ID4", 3),
            _chunk("VW_ID4", 4),
            _chunk("VW_ID4", 5),
        ],
    )
    scored = run_eval.score_question(question, result, 12.0, None, 0, "test")
    assert scored.recall_at_3 is False
    assert scored.recall_at_5 is True
    assert scored.mrr == 0.2


def test_rejection_accuracy_uses_explicit_scope_and_rejects_cited_refusals():
    question = run_eval.TestQuestion(id="r1", question="weather?", should_refuse=True)
    refused = RagResult(answer="خارج النطاق", refused=True, scope="out_of_scope", citations=[])
    scored = run_eval.score_question(question, refused, 1.0, None, 0, "test")
    assert scored.rejection_accuracy is True

    bad = RagResult(
        answer="خارج النطاق",
        refused=True,
        scope="out_of_scope",
        citations=[{"manual_name": "VW_ID4", "page": 1}],
    )
    scored_bad = run_eval.score_question(question, bad, 1.0, None, 0, "test")
    assert scored_bad.rejection_accuracy is False


def test_insufficient_evidence_is_not_out_of_scope_refusal():
    question = run_eval.TestQuestion(id="r1", question="manual?", should_refuse=True)
    result = RagResult(answer="not found", insufficient_evidence=True, citations=[])
    scored = run_eval.score_question(question, result, 1.0, None, 0, "test")
    assert scored.rejection_accuracy is False


def test_summary_reports_warm_and_cold_latency():
    question = run_eval.TestQuestion(id="q", question="manual", manual="VW_ID4", expected_page=1)
    result = RagResult(answer="answer", reranked_chunks=[_chunk("VW_ID4", 1)])
    scored = run_eval.score_question(question, result, 20.0, None, 0, "test")
    summary = run_eval.build_summary([scored], run_eval.ROOT / "test.json", run_eval.ROOT, "test", 0, cold_start_latency_ms=99.0)
    assert summary["avg_warm_latency_ms"] == 20.0
    assert summary["cold_start_latency_ms"] == 99.0
    assert summary["avg_returned_chunks"] == 1.0
