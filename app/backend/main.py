from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.core.config import settings
from app.backend.api.routes import router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
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


@app.get("/")
def root() -> dict:
    return {"project": settings.PROJECT_NAME}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}