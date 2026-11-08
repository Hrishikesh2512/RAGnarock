import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_requires_auth_to_be_enabled() -> None:
    with pytest.raises(ValidationError, match="AUTH_DISABLED"):
        Settings(app_env="production", auth_disabled=True)


def test_auth_requires_a_jwt_secret() -> None:
    with pytest.raises(ValidationError, match="JWT_SECRET"):
        Settings(auth_disabled=False, jwt_secret=None)


def test_development_defaults_are_valid() -> None:
    settings = Settings()

    assert settings.app_env == "development"
    assert settings.auth_disabled is True
    assert settings.embedding_dim == 384
    assert "application/pdf" in settings.allowed_mime_types


def test_allowed_mime_types_accepts_a_comma_separated_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOWED_MIME_TYPES", "application/pdf, text/plain ,")

    settings = Settings()

    assert settings.allowed_mime_types == ["application/pdf", "text/plain"]
