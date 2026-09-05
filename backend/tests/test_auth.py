import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from datetime import timedelta

def test_password_hashing():
    plain = "SuperSecurePassword123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_jwt_token_flow():
    payload = {"sub": "user_abc123", "role": "student"}
    token = create_access_token(payload, expires_delta=timedelta(minutes=30))
    assert isinstance(token, str)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user_abc123"
    assert decoded["role"] == "student"

def test_invalid_jwt_token():
    assert decode_access_token("invalid.token.string") is None
