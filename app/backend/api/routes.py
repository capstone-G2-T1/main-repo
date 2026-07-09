import time

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.backend.db.session import get_db
from app.backend.db.models import QueryLog

from schemas import AskRequest, AskResponse, CitationSchema, QueryLogResponse
from app.backend.core.helpers import _build_chunks_summary

router = APIRouter()


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


    normalized_question: str | None = None
    ner_entities = None
    intent: str | None = None
    metadata_filter = None
    raw_chunks: list[dict] | None = None

    answer     = "الإجابة غير متوفرة بعد — قيد التطوير"
    citations: list[dict] = []
    confidence = "low"


    latency_seconds = round(time.perf_counter() - start_time, 4)

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