from rag.reranker import rerank_chunks
from rag.types import RetrievedChunk


class FakeModel:
    def predict(self, pairs):
        return [0.1, 0.9, 0.4, 0.2, 0.8, 0.3]


class BrokenModel:
    def predict(self, pairs):
        raise RuntimeError("no model")


def chunks(count=6):
    return [RetrievedChunk(str(i), f"text {i}", {"page": i}) for i in range(count)]


def test_reranker_sorts_and_limits():
    result = rerank_chunks("query", chunks(), top_k=5, model_getter=lambda: FakeModel())
    assert [chunk.id for chunk in result] == ["1", "4", "2", "5", "3"]
    assert result[0].reranker_score == 0.9
    assert result[0].metadata["page"] == 1


def test_disabled_mode_preserves_order_without_loading_model():
    result = rerank_chunks("query", chunks(), top_k=5, enabled=False, model_getter=lambda: (_ for _ in ()).throw(AssertionError()))
    assert [chunk.id for chunk in result] == ["0", "1", "2", "3", "4"]


def test_fallback_preserves_vector_order():
    result = rerank_chunks("query", chunks(), top_k=5, model_getter=lambda: BrokenModel())
    assert [chunk.id for chunk in result] == ["0", "1", "2", "3", "4"]
    assert rerank_chunks.last_fallback_used is True


def test_empty_input():
    assert rerank_chunks("query", []) == []
