"""Shared typed values passed between RAG pipeline stages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExtractedEntities:
    """Vehicle and diagnostic entities extracted from a question."""

    make: str | None = None
    model: str | None = None
    trim: str | None = None
    year: int | None = None
    vehicle_system: str | None = None
    error_code: str | None = None

    def as_dict(self) -> dict[str, str | int | None]:
        return {
            "make": self.make,
            "model": self.model,
            "trim": self.trim,
            "year": self.year,
            "vehicle_system": self.vehicle_system,
            "error_code": self.error_code,
        }


@dataclass
class RetrievedChunk:
    """A manual chunk returned by Chroma and optionally reranked."""

    id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    retrieval_score: float | None = None
    reranker_score: float | None = None

    def as_log_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "metadata": self.metadata,
            "retrieval_score": self.retrieval_score,
            "reranker_score": self.reranker_score,
        }
