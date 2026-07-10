"""
app/backend/rag/pipeline.py

RAG pipeline entrypoint used by the `/ask` route.

This wires together the layers described in the README (normalization -> NER
-> intent -> metadata filter -> retrieval -> rerank -> generation). The
individual layers (query_normalizer, ner_extractor, intent_classifier,
retriever, reranker, generator) are tracked separately on the Roadmap and are
not implemented yet, so this module currently returns a safe "not found in
the manual" style stub. Swapping in the real layers later should not require
any change to the `/ask` route itself.
"""

from api.schemas import RagResult
from rag.query_normalizer import normalize_query


def run_rag_pipeline(question: str, selected_vehicle: str | None = None) -> RagResult:
    """
    Placeholder pipeline.

    TODO: replace with the real flow once query_normalizer, ner_extractor,
    intent_classifier, retriever, reranker, and generator are implemented.
    """
    normalized_question = normalize_query(question)

    return RagResult(
        answer="عذرًا، لم يتم تنفيذ نظام البحث في الكتيبات بعد.",
        citations=[],
        confidence="low",
        intent=None,
        entities=None,
        normalized_query=normalized_question,
    )
