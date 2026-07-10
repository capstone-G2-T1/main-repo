from fastapi.testclient import TestClient

from api import routes
from api.schemas import RagResult
from db.session import get_db
from main import app


class FakeDB:
    def __init__(self, fail_commit=False):
        self.fail_commit = fail_commit
        self.added = None

    def add(self, value):
        self.added = value

    def commit(self):
        if self.fail_commit:
            from sqlalchemy.exc import SQLAlchemyError
            raise SQLAlchemyError("log failed")

    def refresh(self, value):
        return None

    def rollback(self):
        return None


def override_db():
    yield FakeDB()


def test_ask_endpoint_with_mocked_pipeline(monkeypatch):
    monkeypatch.setattr(
        routes,
        "run_rag_pipeline",
        lambda **kwargs: RagResult(
            answer="جواب موثوق",
            citations=[{"manual_name": "manual.pdf", "page": 5}],
            confidence="high",
            intent="specification",
            entities={"make": None, "model": None},
            normalized_query="كم ضغط الاطارات",
        ),
    )
    app.dependency_overrides[get_db] = override_db
    try:
        response = TestClient(app).post("/ask", json={"question": "كم ضغط الإطارات؟", "selected_vehicle": None})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["citations"][0]["page"] == 5
    assert response.json()["intent"] == "specification"


def test_ask_rejects_empty_question():
    app.dependency_overrides[get_db] = override_db
    try:
        response = TestClient(app).post("/ask", json={"question": "   "})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 422
