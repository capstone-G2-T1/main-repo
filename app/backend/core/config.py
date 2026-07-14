"""
Application configuration.
 
Loads settings from environment variables (and a local .env file when present)
using pydantic-settings. All other modules should import `settings` from this
file instead of calling os.environ directly, so configuration stays in one
place.
"""
from typing import List
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Dalilak"
    APP_DESCRIPTION: str = (
        "Retrieval-Augmented Generation assistant for vehicle manuals "
        "(BYD, Geely, and VW)."
    )
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
 
    # --- API ---------------------------------------------------------------
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]

    # --- Postgres -----------------------------------------------------------
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "aispire"
    POSTGRES_USER: str = "aispire"
    POSTGRES_PASSWORD: str = "aispire"
    DATABASE_URL: str | None = None

    # --- Chroma (vector store) ---------------------------------------------
    CHROMA_HOST: str = "chroma"
    CHROMA_PORT: int = 8000
    CHROMA_COLLECTION_NAME: str = "vehicle_manuals_ar"
 
    # --- Ollama (local LLM) --------------------------------------------------
    OLLAMA_HOST: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b-instruct" #qwen2.5:2b
    OLLAMA_TIMEOUT_SECONDS: float = 25.0
 
    # --- Embeddings / Reranker ----------------------------------------------
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    RERANKER_MODEL: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
    RERANKER_ENABLED: bool = True
 
    # --- Retrieval -----------------------------------------------------------
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_CANDIDATE_K: int = 20
    RERANKER_TOP_K: int = 5
    MIN_RELEVANCE_SCORE: float = 0.05

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        """Treat common environment names as booleans without weakening other validation."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod"}:
                return False
            if normalized in {"development", "dev"}:
                return True
        return value
 
    # --- JWT settings -----------------------------------------------------------
    SECRET_KEY: str = "b7cf139f3e192b50bd62a617e7264a2a9d12126c5f287e469fa76c04f0b0fd54"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Refresh-token cookie ----------------------------------------------
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"
    REFRESH_TOKEN_COOKIE_SECURE: bool = True
    REFRESH_TOKEN_COOKIE_SAMESITE: str = "lax"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
 
    @property
    def sqlalchemy_database_url(self) -> str:
        """Build the Postgres connection string if DATABASE_URL isn't set explicitly."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
 
 
@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor so the .env file is only parsed once."""
    return Settings()
 
 
settings = get_settings()
