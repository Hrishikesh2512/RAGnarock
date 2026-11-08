"""LLM provider selection."""

from functools import lru_cache

from app.core.config import get_settings
from app.llm.base import LLMProvider
from app.llm.fake import FakeProvider
from app.llm.openrouter import OpenRouterProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_provider == "fake":
        return FakeProvider()
    if settings.llm_provider == "openrouter":
        return OpenRouterProvider()
    raise RuntimeError(f"Unsupported LLM_PROVIDER={settings.llm_provider}")
