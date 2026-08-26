"""
auth/schemas.py
─────────────────────────────────────────────────────────────────────────────
Pydantic request/response schemas for the auth routes.
None of these schemas expose password hashes.
"""

from pydantic import BaseModel, Field


# ── Response: issued after a successful /auth/login or /auth/refresh ───────────
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    must_change_password: bool


# ── Request: POST /auth/change-password ───────────────────────────────────────
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)


# ── Response: GET /auth/me — sanitised user info (no hashes) ──────────────────
class UserAuthOut(BaseModel):
    id: int
    username: str
    role: str
    must_change_password: bool

    class Config:
        from_attributes = True  # allows construction from an ORM model instance


# ── Response: POST /auth/refresh ─────────────────────────────────────────────
class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
