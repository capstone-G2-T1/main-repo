"""
app/backend/api/routes.py

API routes for the Vehicle Manual RAG backend.
"""

import time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.backend.api.schemas import (
    AskRequest,
    AskResponse,
    HealthResponse,
    ManualResponse,
    QueryLogResponse,
)
from db.models import Manual, QueryLog, Vehicle
from db.session import get_db
from app.backend.rag.pipeline import run_rag_pipeline
from app.backend.core.helpers import _build_chunks_summary

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    """Simple liveness check."""
    return HealthResponse(status="ok")


@router.post("/ask", response_model=AskResponse, tags=["rag"])
def ask_question(
    payload: AskRequest,
    db: Session = Depends(get_db),
) -> AskResponse:
    """
    Answer a user question using the RAG pipeline and
    store the interaction for later evaluation.
    """

    if not payload.question.strip():
        raise HTTPException(
            status_code=422,
            detail="question must not be empty",
        )

    start = time.perf_counter()

    result = run_rag_pipeline(
        question=payload.question,
        selected_vehicle=payload.selected_vehicle,
    )

    latency_ms = int((time.perf_counter() - start) * 1000)

    retrieved_chunks = getattr(result, "retrieved_chunks", None)

    vehicle_id = None
    vehicle = None

    if payload.selected_vehicle:
        vehicle = (
            db.query(Vehicle)
            .filter(Vehicle.model.ilike(f"%{payload.selected_vehicle}%"))
            .first()
        )

    if vehicle:
        vehicle_id = vehicle.id
        
    log_entry = QueryLog(
        raw_question=payload.question,
        normalized_question=result.normalized_query,
        vehicle_id=vehicle_id,  
        entities=result.entities,
        intent=result.intent,
        answer=result.answer,
        citations={"items": result.citations},
        confidence=result.confidence,
        latency_seconds=latency_ms / 1000,
        retrieved_chunks=_build_chunks_summary(retrieved_chunks),
    )

    try:
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save query log.",
        )

    return AskResponse(
    answer=result.answer,
    citations=result.citations,
    confidence=result.confidence,
    latency_ms=latency_ms,
    intent=result.intent,
    entities=result.entities,
)


@router.get(
    "/manuals",
    response_model=list[ManualResponse],
    tags=["manuals"],
)
def list_manuals(
    make: str | None = Query(
        default=None,
        description="Filter by vehicle make (e.g. BYD).",
    ),
    model_: str | None = Query(
        default=None,
        alias="model",
        description="Filter by vehicle model.",
    ),
    db: Session = Depends(get_db),
) -> list[Manual]:

    stmt = select(Manual).join(Manual.vehicle)

    if make:
        stmt = stmt.where(Vehicle.make.ilike(make))

    if model_:
        stmt = stmt.where(Vehicle.model.ilike(model_))

    stmt = stmt.order_by(Vehicle.make, Vehicle.model)

    return db.execute(stmt).scalars().all()


@router.get(
    "/logs",
    response_model=list[QueryLogResponse],
    tags=["logs"],
)
def list_query_logs(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[QueryLog]:
    """
    Return recent query logs ordered from newest to oldest.
    """
    stmt = (
        select(QueryLog)
        .order_by(QueryLog.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return db.execute(stmt).scalars().all()