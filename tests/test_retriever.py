from rag.retriever import retrieve_chunks


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
