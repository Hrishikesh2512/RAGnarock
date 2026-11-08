import uuid

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_round_trip() -> None:
    password_hash = hash_password("correct horse battery staple")

    assert verify_password("correct horse battery staple", password_hash)
    assert not verify_password("wrong password", password_hash)


def test_access_token_round_trip(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-secret-that-is-long-enough-32")
    get_settings.cache_clear()
    try:
        user_id = str(uuid.uuid4())

        token = create_access_token(user_id)

        assert decode_access_token(token) == user_id
    finally:
        get_settings.cache_clear()
