"""Clear, testable orchestration for the complete vehicle-manual RAG flow."""

from __future__ import annotations

import logging
import time
from uuid import uuid4

from api.schemas import RagResult
from core.config import settings
from rag.entity_extractor import extract_entities
from rag.generator import generate_answer
from rag.intent_classifier import classify_intent
from rag.metadata_filter import build_metadata_filter, resolve_vehicle
from rag.query_normalizer import normalize_query
from rag.reranker import rerank_chunks
from rag.retriever import retrieve_fused_chunks
from rag.scope_classifier import classify_scope
from rag.types import RetrievedChunk

logger = logging.getLogger("rag.pipeline")

OUT_OF_SCOPE_REFUSAL = (
    "عذرا، أستطيع الإجابة فقط عن المعلومات الموجودة في دليل السيارة المحددة. "
    "هذا السؤال خارج نطاق أدلة المركبات المتاحة."
)
INSUFFICIENT_EVIDENCE_REFUSAL = (
    "لم أجد معلومات كافية في دليل السيارة المحدد للإجابة عن هذا السؤال بدقة. "
    "يرجى إعادة صياغة السؤال أو التأكد من اختيار السيارة الصحيحة."
)


def _confidence(chunks: list[RetrievedChunk], citations: list[dict]) -> str:
    """Use interpretable retrieval/citation signals instead of a fake probability."""
    if not chunks or not citations:
        return "low"
    best = chunks[0].reranker_score if chunks[0].reranker_score is not None else chunks[0].retrieval_score
    if len(chunks) >= 2 and (best is None or best >= settings.MIN_RELEVANCE_SCORE):
        return "high"
    return "medium"


def _has_sufficient_evidence(chunks: list[RetrievedChunk]) -> bool:
    if not chunks:
        return False
    scored = [chunk.retrieval_score for chunk in chunks if chunk.retrieval_score is not None]
    return bool(scored) and max(scored) >= settings.MIN_RELEVANCE_SCORE


def run_rag_pipeline(question: str, selected_vehicle: str | None = None) -> RagResult:
    """Run normalization, extraction, filtering, retrieval, reranking, and generation."""
    started = time.perf_counter()
    request_id = str(uuid4())
    scope = classify_scope(question)
    if scope == "out_of_scope":
        logger.info(
            "rag_query",
            extra={
                "request_id": request_id,
                "selected_vehicle": selected_vehicle,
                "scope": scope,
                "refused": True,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            },
        )
        return RagResult(
            answer=OUT_OF_SCOPE_REFUSAL,
            citations=[],
            confidence="low",
            scope=scope,
            refused=True,
            insufficient_evidence=False,
        )

    normalized = normalize_query(question)
    entities = extract_entities(normalized)
    resolved = resolve_vehicle(selected_vehicle, entities)
    intent = classify_intent(normalized)
    metadata_filter = build_metadata_filter(selected_vehicle, entities)
    retrieved, retrieval_stats = retrieve_fused_chunks(
        question,
        normalized,
        metadata_filter,
        top_k=settings.RETRIEVAL_CANDIDATE_K,
    )
    if not _has_sufficient_evidence(retrieved):
        logger.info(
            "rag_query",
            extra={
                "request_id": request_id,
                "selected_vehicle": selected_vehicle,
                "scope": scope,
                "entities": resolved.as_dict(),
                "metadata_filter": metadata_filter,
                **retrieval_stats,
                "reranker_enabled": settings.RERANKER_ENABLED,
                "reranker_fallback_used": False,
                "final_chunk_count": 0,
                "top_score": None,
                "refused": False,
                "insufficient_evidence": True,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            },
        )
        return RagResult(
            answer=INSUFFICIENT_EVIDENCE_REFUSAL,
            citations=[],
            confidence="low",
            intent=intent,
            entities=resolved.as_dict(),
            normalized_query=normalized,
            metadata_filter=metadata_filter,
            retrieved_chunks=[chunk.as_log_dict() for chunk in retrieved],
            reranked_chunks=[],
            refused=False,
            scope=scope,
            insufficient_evidence=True,
            retrieval_stats=retrieval_stats,
        )

    reranked = rerank_chunks(normalized, retrieved, top_k=settings.RERANKER_TOP_K)
    answer, citations = generate_answer(
        question,
        normalized,
        resolved,
        intent,
        selected_vehicle,
        reranked,
    )
    top_score = None
    if reranked:
        top_score = reranked[0].reranker_score if reranked[0].reranker_score is not None else reranked[0].retrieval_score
    logger.info(
        "rag_query",
        extra={
            "request_id": request_id,
            "selected_vehicle": selected_vehicle,
            "scope": scope,
            "entities": resolved.as_dict(),
            "metadata_filter": metadata_filter,
            **retrieval_stats,
            "reranker_enabled": settings.RERANKER_ENABLED,
            "reranker_fallback_used": getattr(rerank_chunks, "last_fallback_used", False),
            "final_chunk_count": len(reranked),
            "top_score": top_score,
            "refused": False,
            "insufficient_evidence": False,
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        },
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
        refused=False,
        scope=scope,
        insufficient_evidence=False,
        retrieval_stats=retrieval_stats,
    )
