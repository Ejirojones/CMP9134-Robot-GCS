"""
Unit tests for authentication logic.
Tests password hashing and token creation/verification.
"""

import sys

sys.path.insert(0, "/workspace/backend")

from auth import hash_password, verify_password, create_token, verify_token


def test_password_hashing():
    """Password hash should not equal the original password."""
    hashed = hash_password("mypassword")
    assert hashed != "mypassword"


def test_password_verification_correct():
    """Correct password should verify successfully."""
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) == True


def test_password_verification_wrong():
    """Wrong password should fail verification."""
    hashed = hash_password("mypassword")
    assert verify_password("wrongpassword", hashed) == False


def test_token_creation():
    """Token should be created and contain a dot separator."""
    token = create_token("testuser", "commander")
    assert "." in token


def test_token_verification_valid():
    """Valid token should return correct username and role."""
    token = create_token("testuser", "commander")
    payload = verify_token(token)
    assert payload is not None
    assert payload["username"] == "testuser"
    assert payload["role"] == "commander"


def test_token_verification_invalid():
    """Tampered token should return None."""
    token = create_token("testuser", "commander")
    bad_token = token + "tampered"
    assert verify_token(bad_token) is None


def test_token_viewer_role():
    """Viewer token should have viewer role."""
    token = create_token("viewer1", "viewer")
    payload = verify_token(token)
    assert payload["role"] == "viewer"
