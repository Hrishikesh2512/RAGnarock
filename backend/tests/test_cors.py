from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


def test_foreign_origin_mutation_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("AUTH_DISABLED", "false")
    monkeypatch.setenv("JWT_SECRET", "test-secret-that-is-long-enough-32")
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://app.example.com")
    get_settings.cache_clear()
    try:
        client = TestClient(create_app())

        response = client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "password123"},
            headers={"Origin": "https://evil.example"},
        )

        assert response.status_code == 403
        assert response.json()["error"]["code"] == "origin_not_allowed"
    finally:
        get_settings.cache_clear()


def test_health_is_not_blocked_by_origin(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("AUTH_DISABLED", "false")
    monkeypatch.setenv("JWT_SECRET", "test-secret-that-is-long-enough-32")
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://app.example.com")
    get_settings.cache_clear()
    try:
        client = TestClient(create_app())

        response = client.get("/health", headers={"Origin": "https://evil.example"})

        assert response.status_code == 200
    finally:
        get_settings.cache_clear()
