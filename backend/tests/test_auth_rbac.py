"""Authentication, RBAC and CRUD smoke tests against an isolated in-memory database."""

CAMERA_PAYLOAD = {
    "name": "Carrefour Gombe",
    "location": "Boulevard du 30 Juin, Gombe",
    "latitude": -4.3112,
    "longitude": 15.2995,
    "rtsp_url": "rtsp://demo.local/gombe",
    "is_360": True,
}


async def test_login_success(client):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "Admin1234!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


async def test_login_wrong_password(client):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "wrong"},
    )
    assert response.status_code == 401


async def test_me_returns_public_user_without_hashed_password(client, admin_headers):
    response = await client.get("/api/v1/auth/me", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "admin"
    assert body["role"] == "admin"
    assert "hashed_password" not in body


async def test_me_requires_token(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_me_rejects_invalid_token(client):
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


async def test_viewer_cannot_create_camera(client, viewer_headers):
    response = await client.post("/api/v1/cameras/", json=CAMERA_PAYLOAD, headers=viewer_headers)
    assert response.status_code == 403


async def test_admin_can_create_camera(client, admin_headers):
    create_response = await client.post(
        "/api/v1/cameras/", json=CAMERA_PAYLOAD, headers=admin_headers
    )
    assert create_response.status_code == 201, create_response.text

    list_response = await client.get("/api/v1/cameras/", headers=admin_headers)
    assert list_response.status_code == 200
    cameras = list_response.json()
    assert any(camera["name"] == CAMERA_PAYLOAD["name"] for camera in cameras)
    assert all("hashed_password" not in camera for camera in cameras)


async def test_list_cameras_empty_initially(client, admin_headers):
    response = await client.get("/api/v1/cameras/", headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == []


async def test_traffic_zones_accessible_when_authenticated(client, viewer_headers):
    response = await client.get("/api/v1/traffic/zones", headers=viewer_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_vehicles_require_operator_role(client, viewer_headers):
    response = await client.get("/api/v1/vehicles/", headers=viewer_headers)
    assert response.status_code == 403


async def test_vehicles_accessible_to_admin(client, admin_headers):
    response = await client.get("/api/v1/vehicles/", headers=admin_headers)
    assert response.status_code == 200
