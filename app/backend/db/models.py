from sqlalchemy import Column, Integer, Text, Float, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class QueryLog(Base):
    """
    Stores every /ask request with full pipeline output.
    All intermediate fields are nullable — the log is written even
    if the pipeline fails mid-way.
    """
    __tablename__ = "query_logs"

    id                       = Column(Integer, primary_key=True, autoincrement=True)

    # User input
    original_question        = Column(Text, nullable=False)
    selected_vehicle         = Column(Text, nullable=False)

    # Pipeline intermediate outputs
    normalized_question      = Column(Text,  nullable=True)
    ner_entities             = Column(JSONB, nullable=True)
    intent                   = Column(Text,  nullable=True)
    metadata_filter          = Column(JSONB, nullable=True)

    # Retrieval: metadata + first 200 chars per chunk
    retrieved_chunks_summary = Column(JSONB, nullable=True)

    # Final output
    answer                   = Column(Text,  nullable=True)
    citations                = Column(JSONB, nullable=True)
    confidence               = Column(Text,  nullable=True)

    # Performance
    latency_seconds          = Column(Float, nullable=True)

    # Audit
    created_at               = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )