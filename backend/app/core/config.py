"""Application settings, loaded from the environment."""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# v1 parses text only. PDF and DOCX parsers are a later issue.
DEFAULT_MIME_TYPES = (
    "text/plain",
    "text/markdown",
)


class Settings(BaseSettings):
    """Runtime configuration.

    Every field maps to an upper-case environment variable (``app_env`` reads
    ``APP_ENV``). See ``.env.example`` and docs/architecture.md §12.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- core ---
    app_name: str = "RAGnarok"
    app_env: Literal["development", "production", "test"] = "development"
    api_base_url: str = "http://localhost:8000"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["console", "json"] = "console"

    # --- database ---
    database_url: str = "postgresql+psycopg://ragnarok:ragnarok@db:5432/ragnarok"

    # --- http ---
    allowed_origins: Annotated[list[str], NoDecode] = []

    # --- storage ---
    storage_backend: Literal["local", "s3"] = "local"
    storage_path: str = "/data/uploads"
    max_upload_mb: int = 10
    allowed_mime_types: Annotated[list[str], NoDecode] = list(DEFAULT_MIME_TYPES)

    # --- embeddings ---
    embedding_provider: Literal["local", "openrouter", "fake"] = "local"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384
    embedding_batch_size: int = 32

    # --- generation ---
    llm_provider: Literal["openrouter", "ollama", "fake"] = "openrouter"
    llm_model: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    llm_temperature: float = 0.2
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    ollama_base_url: str = "http://ollama:11434"
    allow_server_llm_key: bool = False

    # --- retrieval ---
    retrieval_top_k: int = 8
    retrieval_min_score: float = 0.30
    context_max_tokens: int = 6000

    # --- auth and sessions ---
    auth_disabled: bool = True
    jwt_secret: str | None = None
    jwt_expire_minutes: int = 60
    guest_session_ttl_hours: int = 168
    max_docs_per_session: int = 5

    # --- rate limiting ---
    rate_limit_chat_per_min: int = 10
    rate_limit_upload_per_min: int = 3

    @field_validator("allowed_mime_types", "allowed_origins", mode="before")
    @classmethod
    def _split_csv(cls, value: object) -> object:
        """Accept the comma-separated form used in ``.env`` files.

        ``NoDecode`` stops pydantic-settings from JSON-decoding these variables,
        so ``text/plain,text/markdown`` arrives here as a plain string.
        """
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @model_validator(mode="after")
    def _validate_auth(self) -> "Settings":
        if not self.auth_disabled and not self.jwt_secret:
            raise ValueError("JWT_SECRET is required when AUTH_DISABLED=false")
        if self.is_production and self.auth_disabled:
            raise ValueError("AUTH_DISABLED=true is not allowed when APP_ENV=production")
        if self.is_production and not self.allowed_origins:
            raise ValueError("ALLOWED_ORIGINS is required when APP_ENV=production")
        return self

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings singleton."""
    return Settings()
