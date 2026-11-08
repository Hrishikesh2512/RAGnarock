"""Embedding provider selection."""

from functools import lru_cache

from app.core.config import get_settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.fake import FakeEmbedder
from app.embeddings.local import LocalEmbedder


@lru_cache
def get_embedder() -> EmbeddingProvider:
    settings = get_settings()
    if settings.embedding_provider == "fake":
        return FakeEmbedder(settings.embedding_dim)
    if settings.embedding_provider == "local":
        return LocalEmbedder(
            settings.embedding_model,
            settings.embedding_dim,
            settings.embedding_batch_size,
        )
    raise RuntimeError(f"Unsupported EMBEDDING_PROVIDER={settings.embedding_provider}")
