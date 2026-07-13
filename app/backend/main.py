"""
FastAPI application entrypoint for the Vehicle Manual RAG backend.

Run locally with:
    cd app/backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth import router as auth_router
from api.routes import router
from api.schemas import RootResponse
from core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow the Next.js frontend to call the API, whether it's running via
# Docker (localhost:3000) or a local `npm run dev` (localhost:3001, the
# port Next.js falls back to when 3000 is already taken).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)


@app.get("/", response_model=RootResponse, tags=["system"])
def read_root() -> RootResponse:
    """Returns the project name so a human/monitor can confirm the right service is up."""
    return RootResponse(project=settings.APP_NAME, version=settings.APP_VERSION)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}