"""
auth/security.py
─────────────────────────────────────────────────────────────────────────────
Cryptographic primitives for the auth layer.

Uses `bcrypt` directly (not via passlib) to avoid the passlib 1.7.x ↔
bcrypt >=4.0.0 compatibility bug on Python 3.13 where passlib's internal
wrap-bug detection probe exceeds bcrypt's 72-byte limit.
"""

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import JWTError, jwt
import bcrypt as _bcrypt

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────
SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "fallback-dev-secret-do-not-use-in-prod")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
REFRESH_TOKEN_EXPIRE_DAYS: int = 7

# ── Password hashing (bcrypt directly, bypassing passlib) ─────────────────────
def hash_password(plain: str) -> str:
    """Return a bcrypt hash of the plain-text password."""
    salt = _bcrypt.gensalt(rounds=12)
    return _bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored bcrypt hash."""
    try:
        return _bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ── JWT access token ───────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a signed HS256 JWT.

    The `data` dict is copied and a 'exp' claim is injected.
    Caller should include at minimum: {"sub": username, "role": role}
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT.

    Raises ValueError with a human-readable message on any failure
    (expired, bad signature, malformed). Callers convert this to HTTP 401.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as exc:
        raise ValueError(f"Invalid or expired token: {exc}") from exc


# ── Opaque refresh token ───────────────────────────────────────────────────────
def generate_refresh_token() -> str:
    """
    Generate a cryptographically random 64-hex-character opaque refresh token.
    The raw token is sent to the client as an httpOnly cookie.
    Only its SHA-256 hash is stored in the database.
    """
    return secrets.token_hex(32)  # 256 bits of entropy


def hash_refresh_token(raw_token: str) -> str:
    """Return the SHA-256 hex digest of a raw refresh token for DB storage."""
    return hashlib.sha256(raw_token.encode()).hexdigest()


def verify_refresh_token(raw_token: str, stored_hash: str) -> bool:
    """Constant-time comparison of a raw token against its stored hash."""
    return secrets.compare_digest(
        hash_refresh_token(raw_token), stored_hash
    )
