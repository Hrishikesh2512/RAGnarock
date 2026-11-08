import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_requires_auth_to_be_enabled() -> None:
    with pytest.raises(ValidationError, match="AUTH_DISABLED"):
        Settings(app_env="production", auth_disabled=True)


def test_auth_requires_a_jwt_secret() -> None:
    with pytest.raises(ValidationError, match="JWT_SECRET"):
        Settings(auth_disabled=False, jwt_secret=None)


def test_production_requires_allowed_origins() -> None:
    with pytest.raises(ValidationError, match="ALLOWED_ORIGINS"):
        Settings(
            app_env="production",
            auth_disabled=False,
            jwt_secret="a-long-enough-secret-for-this-test",
            allowed_origins=[],
        )


def test_production_settings_are_valid() -> None:
    settings = Settings(
        app_env="production",
        auth_disabled=False,
        jwt_secret="a-long-enough-secret-for-this-test",
        allowed_origins=["https://app.example.com"],
    )

    assert settings.is_production


def test_development_defaults_are_valid() -> None:
    settings = Settings()

    assert settings.app_env == "development"
    assert settings.auth_disabled is True
    assert settings.embedding_dim == 384
    assert "text/plain" in settings.allowed_mime_types


def test_allowed_mime_types_accepts_a_comma_separated_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOWED_MIME_TYPES", "text/plain, text/markdown ,")

    settings = Settings()

    assert settings.allowed_mime_types == ["text/plain", "text/markdown"]


def test_allowed_origins_accepts_a_comma_separated_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://app.example.com, https://staging.example.com ,")

    settings = Settings()

    assert settings.allowed_origins == [
        "https://app.example.com",
        "https://staging.example.com",
    ]
