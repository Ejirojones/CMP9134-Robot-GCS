"""
Integration tests for API routes.
Tests authentication, RBAC and robot endpoints.
"""

import sys

sys.path.insert(0, "/workspace/backend")

from fastapi.testclient import TestClient
from main import app

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
