from typing import Any
from pydantic import BaseModel, field_validator


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