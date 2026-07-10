"""
FastAPI application entrypoint for the Vehicle Manual RAG backend.
 
Run locally with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import RootResponse
from core.config import settings
from api.routes import router

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow Next.js frontend (localhost:3000) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", response_model=RootResponse, tags=["system"])
def read_root() -> RootResponse:
    """Returns the project name so a human/monitor can confirm the right service is up."""
    return RootResponse(project=settings.APP_NAME, version=settings.APP_VERSION)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
