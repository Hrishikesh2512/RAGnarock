"""OpenRouter chat completions with a request-scoped key."""

import httpx

from app.api.errors import ApiError
from app.core.config import get_settings


class OpenRouterProvider:
    name = "openrouter"

    def generate(self, prompt: str, *, api_key: str | None) -> str:
        if not api_key:
            raise ApiError(
                401,
                "provider_key_required",
                "An OpenRouter key is required. Send it in X-Provider-Key.",
            )

        settings = get_settings()
        url = f"{settings.openrouter_base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": settings.llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": settings.llm_temperature,
        }
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=60.0)
        except httpx.HTTPError as exc:
            raise ApiError(
                502, "provider_unavailable", "The model provider could not be reached."
            ) from exc

        if response.status_code in (401, 403):
            raise ApiError(401, "invalid_provider_key", "The model provider rejected the key.")
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "30")
            raise ApiError(
                429,
                "provider_rate_limited",
                f"The model provider is rate limiting requests. Retry in {retry_after}s.",
                headers={"Retry-After": retry_after},
            )
        if response.status_code >= 500:
            raise ApiError(502, "provider_unavailable", "The model provider returned an error.")
        if response.status_code >= 400:
            raise ApiError(
                502,
                "provider_error",
                "The model provider rejected the request.",
                {"status": response.status_code},
            )

        try:
            return response.json()["choices"][0]["message"]["content"].strip()
        except (AttributeError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ApiError(
                502, "provider_error", "The model provider returned an unexpected response."
            ) from exc
