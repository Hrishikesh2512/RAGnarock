from fastapi.testclient import TestClient

from app import __version__
from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version_reports_build_information() -> None:
    response = client.get("/version")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "RAGnarok"
    assert body["version"] == __version__
    assert body["environment"] == "development"


def test_openapi_is_served_under_api_prefix() -> None:
    response = client.get("/api/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/health" in paths
    assert "/version" in paths
