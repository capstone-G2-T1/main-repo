from rag.retriever import retrieve_chunks, retrieve_fused_chunks


class FakeCollection:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.kwargs = None

    def query(self, **kwargs):
        self.kwargs = kwargs
        if self.error:
            raise self.error
        return self.response


def test_retrieval_parses_chroma_and_applies_filter():
    collection = FakeCollection({
        "ids": [["m1:0"]],
        "documents": [["battery instructions"]],
        "metadatas": [[{"make": "BYD", "model": "Dolphin", "page": 42, "manual_name": "dolphin.pdf"}]],
        "distances": [[0.25]],
    })
    where = {"model": {"$eq": "Dolphin"}}
    chunks = retrieve_chunks("battery", where, collection_getter=lambda: collection, embedder=lambda _: [0.1])
    assert len(chunks) == 1
    assert chunks[0].metadata["page"] == 42
    assert chunks[0].retrieval_score == 0.8
    assert collection.kwargs["where"] == where


def test_empty_or_unavailable_chroma_is_safe():
    empty = FakeCollection({"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]})
    assert retrieve_chunks("q", collection_getter=lambda: empty, embedder=lambda _: [1.0]) == []
    broken = FakeCollection(error=ConnectionError())
    assert retrieve_chunks("q", collection_getter=lambda: broken, embedder=lambda _: [1.0]) == []


class SequencedCollection:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def query(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)


def test_original_and_normalized_candidates_are_fused_without_losing_original():
    collection = SequencedCollection(
        [
            {
                "ids": [["orig"]],
                "documents": [["READY stays visible"]],
                "metadatas": [[{"manual_name": "VW_ID4", "page_number": "10"}]],
                "distances": [[0.1]],
            },
            {
                "ids": [["norm"]],
                "documents": [["normalized candidate"]],
                "metadatas": [[{"manual_name": "VW_ID4", "page": 11}]],
                "distances": [[0.2]],
            },
        ]
    )
    chunks, stats = retrieve_fused_chunks(
        "السؤال الأصلي",
        "السؤال الاصلي",
        top_k=5,
        collection_getter=lambda: collection,
        embedder=lambda _: [0.1],
    )
    assert {chunk.id for chunk in chunks} == {"orig", "norm"}
    assert chunks[0].metadata["page"] == 10
    assert stats == {
        "original_candidate_count": 1,
        "normalized_candidate_count": 1,
        "merged_candidate_count": 2,
    }
