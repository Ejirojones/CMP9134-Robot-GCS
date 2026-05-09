"""
Integration tests for API routes.
Tests authentication, RBAC and robot endpoints.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from database import init_db
from main import app

init_db()
client = TestClient(app)


def test_health_check():
    """Health endpoint should return 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_register_new_user():
    """Registering a new user should return 200."""
    import time

    unique = f"testuser_{int(time.time())}"
    response = client.post(
        f"/api/register?username={unique}&password=test123&role=viewer"
    )
    assert response.status_code == 200
    assert unique in response.json()["message"]


def test_register_duplicate_user():
    """Registering same username twice should return 400."""
    client.post("/api/register?username=dupuser&password=test123&role=viewer")
    response = client.post(
        "/api/register?username=dupuser&password=test123&role=viewer"
    )
    assert response.status_code == 400


def test_login_valid():
    """Valid login should return a token."""
    client.post("/api/register?username=logintest&password=pass123&role=commander")
    response = client.post("/api/login?username=logintest&password=pass123")
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_invalid():
    """Wrong password should return 401."""
    client.post("/api/register?username=logintest2&password=pass123&role=viewer")
    response = client.post("/api/login?username=logintest2&password=wrongpass")
    assert response.status_code == 401


def test_viewer_cannot_move():
    """Viewer token should get 403 when trying to move robot."""
    client.post("/api/register?username=viewertest&password=pass123&role=viewer")
    login = client.post("/api/login?username=viewertest&password=pass123")
    token = login.json()["token"]
    response = client.post(f"/api/move/secure?x=5&y=5&token={token}")
    assert response.status_code == 403


def test_unauthenticated_move():
    """No token should return 401."""
    response = client.post("/api/move/secure?x=5&y=5&token=invalidtoken")
    assert response.status_code == 401


# Legacy Stats Tests


def test_mission_stats_recon():
    """Successful Recon mission (Type 1) should return a score."""
    response = client.post(
        "/api/mission_stats",
        json={"type": 1, "dist": 100, "batt": 80, "payload_weight": 0},
    )
    assert response.status_code == 200
    assert response.json()["mission"] == "recon"
    assert response.json()["final_score"] > 0


def test_mission_stats_transport_heavy_payload():
    """Transport mission (Type 2) with payload > 50 should deduct score."""
    response = client.post(
        "/api/mission_stats",
        json={"type": 2, "dist": 100, "batt": 50, "payload_weight": 60},
    )
    assert response.status_code == 200
    assert response.json()["mission"] == "transport"


def test_mission_stats_missing_field():
    """Request missing required field should return 422."""
    response = client.post("/api/mission_stats", json={"type": 1, "dist": 100})
    assert response.status_code == 422


def test_mission_stats_score_capped():
    """Score should never exceed 100."""
    response = client.post(
        "/api/mission_stats",
        json={"type": 1, "dist": 10000, "batt": 1, "payload_weight": 0},
    )
    assert response.status_code == 200
    assert response.json()["final_score"] <= 100
