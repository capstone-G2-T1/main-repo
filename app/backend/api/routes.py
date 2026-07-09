import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.backend.db.session import get_db
from app.backend.db.models import QueryLog

router = APIRouter()


# =============================================================
# Request / Response schemas
# =============================================================

class AskRequest(BaseModel):
    question: str
    selected_vehicle: str

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("السؤال لا يمكن أن يكون فارغاً")
        return v.strip()

    @field_validator("selected_vehicle")
    @classmethod
    def vehicle_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("يجب اختيار سيارة")
        return v.strip()


class CitationSchema(BaseModel):
    manual_name: str
    page: int
    section: str | None = None


class AskResponse(BaseModel):
    answer: str
    citations: list[CitationSchema]
    confidence: str
    latency_seconds: float


class QueryLogResponse(BaseModel):
    id: int
    original_question: str
    selected_vehicle: str
    normalized_question: str | None
    ner_entities: Any | None
    intent: str | None
    metadata_filter: Any | None
    retrieved_chunks_summary: Any | None
    answer: str | None
    citations: Any | None
    confidence: str | None
    latency_seconds: float | None
    created_at: str

    class Config:
        from_attributes = True


# =============================================================
# Helper — build retrieved_chunks_summary
# =============================================================

def _build_chunks_summary(chunks: list[dict] | None) -> list[dict] | None:
    """
    Returns metadata + first 200 chars of text for each chunk.
    Returns None safely when chunks is empty or None.
    """
    if not chunks:
        return None

    summary = []
    for chunk in chunks:
        summary.append({
            "manual_name": chunk.get("manual_name"),
            "page":        chunk.get("page"),
            "section":     chunk.get("section"),
            "score":       chunk.get("score"),
            "text_preview": (chunk.get("text") or "")[:200],
        })
    return summary


# =============================================================
# POST /ask
# =============================================================

@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, db: Session = Depends(get_db)) -> AskResponse:
    """
    Main RAG endpoint.
    Receives an Arabic question + selected vehicle, runs the pipeline,
    saves the full log to Postgres, and returns the grounded answer.

    NOTE: The actual RAG pipeline components (normalizer, NER, retriever,
    generator) are not implemented yet. This endpoint saves the log
    and returns a placeholder until those stories are complete.
    """
    start_time = time.perf_counter()

    # ------------------------------------------------------------------
    # TODO (Story 14): normalize question
    # ------------------------------------------------------------------
    normalized_question: str | None = None

    # ------------------------------------------------------------------
    # TODO (Story 15): extract NER entities
    # ------------------------------------------------------------------
    ner_entities: dict | None = None

    # ------------------------------------------------------------------
    # TODO (Story 16): classify intent
    # ------------------------------------------------------------------
    intent: str | None = None

    # ------------------------------------------------------------------
    # TODO (Story 17): build metadata filter
    # ------------------------------------------------------------------
    metadata_filter: dict | None = None

    # ------------------------------------------------------------------
    # TODO (Story 18–19): retrieve + rerank chunks
    # ------------------------------------------------------------------
    raw_chunks: list[dict] | None = None

    # ------------------------------------------------------------------
    # TODO (Story 20): generate grounded answer
    # ------------------------------------------------------------------
    answer     = "الراوية غير متوفرة بعد — قيد التطوير"
    citations: list[dict] = []
    confidence = "low"

    # ------------------------------------------------------------------
    # Measure latency
    # ------------------------------------------------------------------
    latency_seconds = round(time.perf_counter() - start_time, 4)

    # ------------------------------------------------------------------
    # Save query log — always runs, even on partial pipeline output
    # ------------------------------------------------------------------
    log = QueryLog(
        original_question        = request.question,
        selected_vehicle         = request.selected_vehicle,
        normalized_question      = normalized_question,
        ner_entities             = ner_entities,
        intent                   = intent,
        metadata_filter          = metadata_filter,
        retrieved_chunks_summary = _build_chunks_summary(raw_chunks),
        answer                   = answer,
        citations                = citations,
        confidence               = confidence,
        latency_seconds          = latency_seconds,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return AskResponse(
        answer          = answer,
        citations       = [CitationSchema(**c) for c in citations],
        confidence      = confidence,
        latency_seconds = latency_seconds,
    )


# =============================================================
# GET /query-logs
# =============================================================

@router.get("/query-logs", response_model=list[QueryLogResponse])
def get_query_logs(
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[QueryLogResponse]:
    """
    Returns the most recent query logs.
    Default: last 50. Configurable via ?limit=N (max 500).
    """
    logs = (
        db.query(QueryLog)
        .order_by(QueryLog.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        QueryLogResponse(
            **{c.name: getattr(log, c.name) for c in QueryLog.__table__.columns
               if c.name != "created_at"},
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]