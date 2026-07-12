from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, SmallInteger, Text
from sqlalchemy import String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base


user_role_enum = Enum("admin", "user", name="user_role", create_type=False)
language_code_enum = Enum("ar", "en", name="language_code", create_type=False)
intent_type_enum = Enum(
    "warning_light",
    "maintenance",
    "troubleshooting",
    "settings",
    "safety",
    "specification",
    "general_manual_question",
    name="intent_type",
    create_type=False,
)
system_variant_enum = Enum(
    "baseline_vector_rag",
    "rag_normalization",
    "rag_ner_filtering",
    "rag_reranker",
    "full_system",
    name="system_variant",
    create_type=False,
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(
        user_role_enum, nullable=False, server_default=text("'user'")
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("TRUE")
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    sessions: Mapped[list[UserSession]] = relationship(back_populates="user")


class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        UniqueConstraint(
            "make", "model", "trim", "year", name="vehicles_unique_make_model_trim_year"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    make: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    trim: Mapped[str | None] = mapped_column(String(100))
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    sessions: Mapped[list[UserSession]] = relationship(back_populates="vehicle")
    manuals: Mapped[list[Manual]] = relationship(
        back_populates="vehicle", cascade="all, delete-orphan"
    )
    query_logs: Mapped[list[QueryLog]] = relationship(back_populates="vehicle")
    eval_questions: Mapped[list[EvalQuestion]] = relationship(back_populates="vehicle")


class Manual(Base):
    __tablename__ = "manuals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False
    )
    manual_name: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(language_code_enum, nullable=False)
    checksum: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    is_translated: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )
    source_path: Mapped[str | None] = mapped_column(Text)
    translated_path: Mapped[str | None] = mapped_column(Text)
    total_pages: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    vehicle: Mapped[Vehicle] = relationship(back_populates="manuals")
    chunks: Mapped[list[ManualChunk]] = relationship(
        back_populates="manual", cascade="all, delete-orphan"
    )
    eval_questions: Mapped[list[EvalQuestion]] = relationship(back_populates="manual")


class ManualChunk(Base):
    __tablename__ = "manual_chunks"
    __table_args__ = (
        UniqueConstraint(
            "manual_id", "chunk_index", name="manual_chunks_unique_manual_chunk"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    manual_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("manuals.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    section: Mapped[str | None] = mapped_column(String(255))
    chunk_text: Mapped[str | None] = mapped_column(Text)
    chroma_vector_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    manual: Mapped[Manual] = relationship(back_populates="chunks")


class UserSession(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="SET NULL")
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    user: Mapped[User | None] = relationship(back_populates="sessions")
    vehicle: Mapped[Vehicle | None] = relationship(back_populates="sessions")
    query_logs: Mapped[list[QueryLog]] = relationship(back_populates="session")


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="SET NULL")
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="SET NULL")
    )
    raw_question: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_question: Mapped[str | None] = mapped_column(Text)
    intent: Mapped[str | None] = mapped_column(intent_type_enum)
    entities: Mapped[dict | None] = mapped_column(JSONB)
    metadata_filter: Mapped[dict | None] = mapped_column(JSONB)
    retrieved_chunks: Mapped[list | dict | None] = mapped_column(JSONB)
    answer: Mapped[str | None] = mapped_column(Text)
    citations: Mapped[list | dict | None] = mapped_column(JSONB)
    confidence: Mapped[str | None] = mapped_column(String(50))
    latency_seconds: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    session: Mapped[UserSession | None] = relationship(back_populates="query_logs")
    vehicle: Mapped[Vehicle | None] = relationship(back_populates="query_logs")


class EvalQuestion(Base):
    __tablename__ = "eval_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="SET NULL")
    )
    manual_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("manuals.id", ondelete="SET NULL")
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    expected_page: Mapped[int | None] = mapped_column(Integer)
    expected_answer_substring: Mapped[str | None] = mapped_column(Text)
    expected_intent: Mapped[str | None] = mapped_column(intent_type_enum)
    expected_system: Mapped[str | None] = mapped_column(String(100))
    should_refuse: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    vehicle: Mapped[Vehicle | None] = relationship(back_populates="eval_questions")
    manual: Mapped[Manual | None] = relationship(back_populates="eval_questions")
    results: Mapped[list[EvalResult]] = relationship(back_populates="eval_question")


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    run_name: Mapped[str] = mapped_column(String(255), nullable=False)
    system_variant: Mapped[str] = mapped_column(system_variant_enum, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    results: Mapped[list[EvalResult]] = relationship(
        back_populates="eval_run", cascade="all, delete-orphan"
    )


class EvalResult(Base):
    __tablename__ = "eval_results"
    __table_args__ = (
        UniqueConstraint(
            "eval_run_id",
            "eval_question_id",
            name="eval_results_unique_run_question",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    eval_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("eval_runs.id", ondelete="CASCADE"), nullable=False
    )
    eval_question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("eval_questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_correct_retrieval: Mapped[bool | None] = mapped_column(Boolean)
    is_grounded: Mapped[bool | None] = mapped_column(Boolean)
    citation_accuracy: Mapped[bool | None] = mapped_column(Boolean)
    rejection_accuracy: Mapped[bool | None] = mapped_column(Boolean)
    recall_at_3: Mapped[bool | None] = mapped_column(Boolean)
    recall_at_5: Mapped[bool | None] = mapped_column(Boolean)
    mrr: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    latency_seconds: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    retrieved_pages: Mapped[list | dict | None] = mapped_column(JSONB)
    returned_citations: Mapped[list | dict | None] = mapped_column(JSONB)
    generated_answer: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    eval_run: Mapped[EvalRun] = relationship(back_populates="results")
    eval_question: Mapped[EvalQuestion] = relationship(back_populates="results")