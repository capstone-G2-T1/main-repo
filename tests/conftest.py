"""pytest configuration for auth tests."""

import sys
from unittest.mock import MagicMock

# Mock heavy dependencies that aren't needed for auth tests
_HEAVY = [
    "chromadb",
    "sentence_transformers",
    "ollama",
    "pdfplumber",
    "pytesseract",
    "pdf2image",
    "pdf2image.exceptions",
    "torch",
    "transformers",
    "sklearn",
    "rank_bm25",
    "langchain",
    "langchain_community",
    "langchain_text_splitters",
]
for _mod in _HEAVY:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.backend.db.session import Base, get_db
from app.backend.db.models import User, UserSession
from app.backend.main import app

# ── In-memory SQLite ──────────────────────────────────────────────────────────
SQLITE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create only auth-related tables
User.__table__.create(bind=engine, checkfirst=True)
UserSession.__table__.create(bind=engine, checkfirst=True)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    """Register a user and return the response."""
    client.post(
        "/auth/register",
        json={"email": "test@aispire.io", "password": "Secure123"},
    )
    return {"email": "test@aispire.io", "password": "Secure123"}


@pytest.fixture
def auth_token(client, registered_user):
    """Login and return access + refresh tokens."""
    response = client.post("/auth/login", json=registered_user)
    return response.json()