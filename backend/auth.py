"""
Authentication helpers.
Handles password hashing and JWT tokens.
"""

import hashlib
import hmac
import os
import time
import json
import base64

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-change-in-production")


def hash_password(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Check a password against its hash."""
    return hmac.compare_digest(hash_password(password), hashed)


def create_token(username: str, role: str) -> str:
    """Create a simple signed token."""
    payload = {
        "username": username,
        "role": role,
        "exp": time.time() + 86400,  # expires in 24 hours
    }
    data = base64.b64encode(json.dumps(payload).encode()).decode()
    signature = hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()
    return f"{data}.{signature}"


def verify_token(token: str) -> dict | None:
    """Verify token and return payload, or None if invalid."""
    try:
        data, signature = token.rsplit(".", 1)
        expected = hmac.new(
            SECRET_KEY.encode(), data.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        payload = json.loads(base64.b64decode(data).decode())
        if payload["exp"] < time.time():
            return None
        return payload
    except Exception:
        return None


def get_current_user(token: str) -> dict | None:
    """Get user from token."""
    return verify_token(token)
