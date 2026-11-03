from io import BytesIO

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from rodplanner.api.app import app

client = TestClient(app)


def _png_bytes(h: int = 100, w: int = 100) -> bytes:
    """Encode a synthetic floor plan image as PNG bytes."""
    img = np.full((h, w), 255, dtype=np.uint8)
    img[10:90, 10:90] = 0
    _, buf = cv2.imencode(".png", img)
    return buf.tobytes()


# ── health ────────────────────────────────────────────────────────────────────

def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ── analyse: happy path ───────────────────────────────────────────────────────

def test_analyse_200() -> None:
    r = client.post(
        "/analyse",
        files={"image": ("plan.png", BytesIO(_png_bytes()), "image/png")},
    )
    assert r.status_code == 200


def test_analyse_response_shape() -> None:
    r = client.post(
        "/analyse",
        files={"image": ("plan.png", BytesIO(_png_bytes()), "image/png")},
    )
    data = r.json()
    assert "polygon" in data
    assert "rods" in data
    assert "coverage_fraction" in data
    assert "rod_count" in data
    assert "area_m2" in data


def test_analyse_full_coverage() -> None:
    r = client.post(
        "/analyse",
        files={"image": ("plan.png", BytesIO(_png_bytes()), "image/png")},
    )
    assert r.json()["coverage_fraction"] == pytest.approx(1.0)


def test_analyse_custom_height() -> None:
    short = client.post(
        "/analyse?height=2.0",
        files={"image": ("plan.png", BytesIO(_png_bytes()), "image/png")},
    )
    tall = client.post(
        "/analyse?height=8.0",
        files={"image": ("plan.png", BytesIO(_png_bytes()), "image/png")},
    )
    assert tall.json()["rod_count"] <= short.json()["rod_count"]


# ── analyse: error paths ──────────────────────────────────────────────────────

def test_analyse_blank_image_422() -> None:
    blank = np.full((100, 100), 255, dtype=np.uint8)
    _, buf = cv2.imencode(".png", blank)
    r = client.post(
        "/analyse",
        files={"image": ("blank.png", BytesIO(buf.tobytes()), "image/png")},
    )
    assert r.status_code == 422


def test_analyse_invalid_file_422() -> None:
    r = client.post(
        "/analyse",
        files={"image": ("bad.png", BytesIO(b"not an image"), "image/png")},
    )
    assert r.status_code == 422


def test_analyse_invalid_height_422() -> None:
    r = client.post(
        "/analyse?height=-1",
        files={"image": ("plan.png", BytesIO(_png_bytes()), "image/png")},
    )
    assert r.status_code == 422
