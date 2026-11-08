"""LLM provider interface."""

from typing import Protocol


class LLMProvider(Protocol):
    name: str

    def generate(self, prompt: str, *, api_key: str | None) -> str: ...
