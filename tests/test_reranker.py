from rag.reranker import rerank_chunks
from rag.types import RetrievedChunk


class FakeModel:
    def predict(self, pairs):
        return [0.1, 0.9, 0.4]


def chunks():
    return [RetrievedChunk(str(i), f"text {i}") for i in range(3)]


def test_reranker_sorts_and_limits():
    result = rerank_chunks("query", chunks(), top_k=2, model_getter=lambda: FakeModel())
    assert [chunk.id for chunk in result] == ["1", "2"]
    assert result[0].reranker_score == 0.9


def test_disabled_mode_preserves_order_without_loading_model():
    result = rerank_chunks("query", chunks(), top_k=2, enabled=False, model_getter=lambda: (_ for _ in ()).throw(AssertionError()))
    assert [chunk.id for chunk in result] == ["0", "1"]


def test_empty_input():
    assert rerank_chunks("query", []) == []
