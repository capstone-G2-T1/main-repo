"""
app/backend/api/schemas.py

API schemas for the Vehicle Manual RAG backend.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Any, Optional

from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = "ok"
 
class RootResponse(BaseModel):
    project: str
    version: str
    docs_url: str = "/docs"

class AskRequest(BaseModel):
    question: str = Field(..., description="User question in Arabic.")
    selected_vehicle: str | None = Field(
        default=None, description="Optional vehicle the user has selected, e.g. 'BYD Dolphin'."
    )


class Citation(BaseModel):
    manual_name: str
    page: int
    section: str | None = None


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: str = "low"
    latency_ms: float
    intent: str | None = None
    entities: dict | None = None 

class QueryLogResponse(BaseModel):
    id: UUID
    session_id: UUID | None = None
    vehicle_id: UUID | None = None

    raw_question: str
    normalized_question: str | None = None

    intent: str | None = None
    entities: dict[str, Any] | None = None

    metadata_filter: dict[str, Any] | None = None
    retrieved_chunks: list[Any] | dict[str, Any] | None = None

    answer: str | None = None
    citations: list[Any] | dict[str, Any] | None = None
    confidence: str | None = None

    latency_seconds: Decimal | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

class VehicleResponse(BaseModel):
    make: str
    model: str
    trim: str | None = None
    year: int

    model_config = {"from_attributes": True}


class ManualResponse(BaseModel):
    id: UUID
    manual_name: str
    language: str
    page_count: int | None
    vehicle: VehicleResponse

    model_config = {"from_attributes": True}

class RagResult(BaseModel):
    answer: str
    citations: list[dict] = Field(default_factory=list)
    confidence: str = "low"
    intent: str | None = None
    entities: dict | None = None
    normalized_query: str | None = None


class ManualMetadata(BaseModel):
    # --- populated by manual_loader.py from the folder/filename ---
    make: str
    model: str
    year: Optional[str]
    file_path: str
 
    # --- populated by pdf_parser.py ---
    total_pages: Optional[int] = None
    ocr_page_count: int = 0
    extraction_errors: list[str] = Field(default_factory=list)
 
    # --- populated by language_detector.py ---
    language: str = "en"
 
    # --- populated by translator.py ---
    is_translated: bool = False
    translated_path: Optional[str] = None