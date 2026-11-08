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
