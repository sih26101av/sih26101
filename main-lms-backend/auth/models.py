"""
auth/models.py
─────────────────────────────────────────────────────────────────────────────
SQLAlchemy model for the users_auth table.

This table is the ONLY persistence concern for authentication.
It is intentionally decoupled from the domain models (models/models.py).

Columns
───────
id                 – Integer PK, autoincrement
username           – the usr_XXXXXXXXX userId from the iGOT mock server
                     (also "admin" for the built-in admin user)
password_hash      – bcrypt hash via passlib
role               – "learner" | "admin"
must_change_password – True for all auto-seeded users; False for admin
refresh_token_hash – nullable; stores SHA-256 of the current refresh token
                     (nulled out on logout / rotation)
"""

from sqlalchemy import Boolean, Column, Integer, String
from .database import AuthBase


class UserAuth(AuthBase):
    __tablename__ = "users_auth"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # The iGOT userId becomes the login username (e.g. "usr_720465595")
    username = Column(String, unique=True, nullable=False, index=True)

    password_hash = Column(String, nullable=False)

    # "learner" or "admin" — kept as a plain String for simplicity;
    # an Enum would be cleaner but adds migration friction for a prototype.
    role = Column(String, nullable=False, default="learner")

    # Forces a password change on first login for all auto-seeded accounts
    must_change_password = Column(Boolean, nullable=False, default=True)

    # Stored as a hash so the raw token is never persisted.
    # Null means "no active session" (logged out).
    refresh_token_hash = Column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<UserAuth username={self.username!r} role={self.role!r}>"
