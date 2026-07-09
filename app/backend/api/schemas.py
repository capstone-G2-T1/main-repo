import time

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.backend.db.models import QueryLog
from app.backend.db.session import get_db

from app.backend.api.schemas import (
    AskRequest,
    AskResponse,
    CitationSchema,
    QueryLogResponse,
)

router = APIRouter()


def _build_chunks_summary(chunks: list[dict] | None) -> list[dict] | None:
    if not chunks:
        return None

    summary = []

    for chunk in chunks:
        summary.append({
            "manual_name": chunk.get("manual_name"),
            "page": chunk.get("page"),
            "section": chunk.get("section"),
            "score": chunk.get("score"),
            "text_preview": (chunk.get("text") or "")[:200],
        })

    return summary


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, db: Session = Depends(get_db)):

    start_time = time.perf_counter()

    # Placeholder values until RAG is implemented
    normalized_question = request.question
    ner_entities = None
    intent = None
    metadata_filter = None
    raw_chunks = []

    answer = "الراوية غير متوفرة بعد — قيد التطوير"
    citations = []
    confidence = "low"

    latency_seconds = round(time.perf_counter() - start_time, 4)

    log = QueryLog(
        original_question=request.question,
        selected_vehicle=request.selected_vehicle,
        normalized_question=normalized_question,
        ner_entities=ner_entities,
        intent=intent,
        metadata_filter=metadata_filter,
        retrieved_chunks_summary=_build_chunks_summary(raw_chunks),
        answer=answer,
        citations=citations,
        confidence=confidence,
        latency_seconds=latency_seconds,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return AskResponse(
        answer=answer,
        citations=[CitationSchema(**c) for c in citations],
        confidence=confidence,
        latency_seconds=latency_seconds,
    )


@router.get("/query-logs", response_model=list[QueryLogResponse])
def get_query_logs(
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):

    logs = (
        db.query(QueryLog)
        .order_by(QueryLog.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        QueryLogResponse(
            **{
                c.name: getattr(log, c.name)
                for c in QueryLog.__table__.columns
                if c.name != "created_at"
            },
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]