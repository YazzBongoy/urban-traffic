"""Tests de l'endpoint d'analyse vision (POST /cameras/{id}/analyze).

Les tests binaires sont skippés si les poids ML ne sont pas présents (CI).
"""

import io
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.services.vision import models_available  # noqa: E402

pytestmark = pytest.mark.skipif(
    not models_available(), reason="Poids ML absents (ml/models/)"
)


def _jpeg_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (320, 200), color=(40, 40, 40)).save(buf, format="JPEG")
    return buf.getvalue()


async def _create_camera(client, admin_headers) -> int:
    response = await client.post(
        "/api/v1/cameras/",
        json={
            "name": "CAM-TEST-01",
            "location": "Boulevard du 30 Juin",
            "latitude": -4.3112,
            "longitude": 15.2995,
            "rtsp_url": "rtsp://demo.local/test",
            "is_360": True,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def test_analyze_returns_structured_result(client, admin_headers):
    camera_id = await _create_camera(client, admin_headers)
    response = await client.post(
        f"/api/v1/cameras/{camera_id}/analyze",
        files={"file": ("frame.jpg", _jpeg_bytes(), "image/jpeg")},
        headers=admin_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["camera_id"] == camera_id
    assert isinstance(body["detections"], list)
    assert body["count"] == len(body["detections"])


async def test_analyze_unknown_camera_404(client, admin_headers):
    response = await client.post(
        "/api/v1/cameras/9999/analyze",
        files={"file": ("frame.jpg", _jpeg_bytes(), "image/jpeg")},
        headers=admin_headers,
    )
    assert response.status_code == 404


async def test_analyze_requires_operator(client, viewer_headers):
    response = await client.post(
        "/api/v1/cameras/1/analyze",
        files={"file": ("frame.jpg", _jpeg_bytes(), "image/jpeg")},
        headers=viewer_headers,
    )
    assert response.status_code == 403


async def test_analyze_rejects_empty_file(client, admin_headers):
    camera_id = await _create_camera(client, admin_headers)
    response = await client.post(
        f"/api/v1/cameras/{camera_id}/analyze",
        files={"file": ("frame.jpg", b"", "image/jpeg")},
        headers=admin_headers,
    )
    assert response.status_code == 400
