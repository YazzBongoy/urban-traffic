"""Smoke tests: application starts and serves core health endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_app_starts_and_serves_docs():
    response = client.get("/docs")
    assert response.status_code == 200


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "version" in body


def test_liveness_endpoint():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_protected_endpoints_reject_anonymous():
    """All routers except /auth must require a JWT (P0 security fix)."""
    for path in (
        "/api/v1/cameras/",
        "/api/v1/vehicles/",
        "/api/v1/traffic/realtime",
        "/api/v1/traffic/zones",
        "/api/v1/analytics/statistics",
    ):
        response = client.get(path)
        assert response.status_code == 401, f"{path} is not protected"


def test_login_requires_credentials():
    response = client.post("/api/v1/auth/login", data={"username": "x", "password": "y"})
    assert response.status_code in (401, 500)
