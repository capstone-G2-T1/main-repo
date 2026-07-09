"""
Entry point for the AI.SPIRE backend (FastAPI).
For Story 1, this only needs to expose the app and prove the service
is reachable on http://localhost:8000. Routes for /ask, ingestion, etc.
get wired in as their own stories are implemented.
"""

from fastapi import FastAPI

app = FastAPI(
    title="AI.SPIRE — Vehicle Manual RAG API",
    description="Backend service for the Chinese vehicle manual RAG assistant.",
    version="0.1.0",
)


@app.get("/")
def read_root():
    """Basic root route so the API responds on GET /."""
    return {"status": "ok", "service": "aispire-backend"}


@app.get("/health")
def health_check():
    """Health check endpoint used by Docker/monitoring to confirm the
    backend container came up correctly."""
    return {"status": "healthy"}
