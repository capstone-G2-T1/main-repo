"""Clear, testable orchestration for the complete vehicle-manual RAG flow."""

from __future__ import annotations

from api.schemas import RagResult
from rag.entity_extractor import extract_entities
from rag.generator import generate_answer
from rag.intent_classifier import classify_intent
from rag.metadata_filter import build_metadata_filter, resolve_vehicle
from rag.query_normalizer import normalize_query
from rag.reranker import rerank_chunks
from rag.retriever import retrieve_chunks
from rag.types import RetrievedChunk


def _confidence(chunks: list[RetrievedChunk], citations: list[dict]) -> str:
    """Use interpretable retrieval/citation signals instead of a fake probability."""
    if not chunks or not citations:
        return "low"
    best = chunks[0].reranker_score
    if len(chunks) >= 2 and (best is None or best >= 0.25):
        return "high"
    return "medium"


def run_rag_pipeline(question: str, selected_vehicle: str | None = None) -> RagResult:
    """Run normalization, extraction, filtering, retrieval, reranking, and generation."""
    normalized = normalize_query(question)
    entities = extract_entities(normalized)
    resolved = resolve_vehicle(selected_vehicle, entities)
    intent = classify_intent(normalized)
    metadata_filter = build_metadata_filter(selected_vehicle, entities)
    retrieved = retrieve_chunks(normalized, metadata_filter)
    reranked = rerank_chunks(normalized, retrieved)
    answer, citations = generate_answer(
        question,
        normalized,
        resolved,
        intent,
        selected_vehicle,
        reranked,
    )

    return RagResult(
        answer=answer,
        citations=citations,
        confidence=_confidence(reranked, citations),
        intent=intent,
        entities=resolved.as_dict(),
        normalized_query=normalized,
        metadata_filter=metadata_filter,
        retrieved_chunks=[chunk.as_log_dict() for chunk in retrieved],
        reranked_chunks=[chunk.as_log_dict() for chunk in reranked],
    )
