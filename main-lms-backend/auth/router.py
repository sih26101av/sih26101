"""
auth/router.py
─────────────────────────────────────────────────────────────────────────────
FastAPI router exposing all /auth/* endpoints.

Endpoints
─────────
POST /auth/login           – OAuth2 password grant; issues JWT + sets refresh cookie
POST /auth/refresh         – Validates refresh cookie; issues new access token
POST /auth/logout          – Invalidates refresh token hash; clears cookie
POST /auth/change-password – Authenticated; changes password; clears must_change flag
GET  /auth/me              – Authenticated; returns sanitised user info

Refresh token strategy
──────────────────────
The raw refresh token is sent as an httpOnly, Secure, SameSite=Strict cookie.
Only its SHA-256 hash is stored in the database (refresh_token_hash column).
This means even if the DB is compromised, attackers cannot forge sessions.
"""

from datetime import timedelta

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .database import get_db
from .dependencies import get_current_user
from .models import UserAuth
from .schemas import ChangePasswordRequest, RefreshResponse, TokenResponse, UserAuthOut
from .security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    hash_password,
    verify_password,
    verify_refresh_token,
)

router = APIRouter()

_REFRESH_COOKIE_NAME = "refresh_token"
_REFRESH_COOKIE_MAX_AGE = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # seconds


def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    """Attaches the httpOnly refresh token cookie to the response."""
    response.set_cookie(
        key=_REFRESH_COOKIE_NAME,
        value=raw_token,
        max_age=_REFRESH_COOKIE_MAX_AGE,
        httponly=True,
        secure=False,   # Set True in production (requires HTTPS)
        samesite="strict",
        path="/auth",   # Scoped to /auth/* so the cookie is not sent on every API call
    )


def _clear_refresh_cookie(response: Response) -> None:
    """Removes the refresh token cookie."""
    response.delete_cookie(
        key=_REFRESH_COOKIE_NAME,
        path="/auth",
        httponly=True,
        samesite="strict",
    )


# ── POST /auth/login ───────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate a user with username + password.

    On success:
    - Returns a short-lived JWT access token in the response body.
    - Sets a long-lived refresh token as an httpOnly cookie.
    - Includes the must_change_password flag so the frontend can force redirect.
    """
    # 1. Look up the user
    user: UserAuth | None = (
        db.query(UserAuth).filter(UserAuth.username == form_data.username).first()
    )

    # 2. Validate credentials (deliberately vague error to prevent user enumeration)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Issue JWT access token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    # 4. Generate refresh token, store only its hash
    raw_refresh = generate_refresh_token()
    user.refresh_token_hash = hash_refresh_token(raw_refresh)
    db.commit()

    # 5. Set the refresh cookie
    _set_refresh_cookie(response, raw_refresh)

    return TokenResponse(
        access_token=access_token,
        must_change_password=user.must_change_password,
    )


# ── POST /auth/refresh ─────────────────────────────────────────────────────────
@router.post("/refresh", response_model=RefreshResponse)
def refresh_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=_REFRESH_COOKIE_NAME),
    db: Session = Depends(get_db),
) -> RefreshResponse:
    """
    Exchange a valid refresh token cookie for a new JWT access token.

    The refresh token cookie is validated against the stored hash.
    A new refresh token is NOT issued on refresh (simple rotation strategy:
    the existing cookie keeps its original expiry).
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token. Please log in again.",
    )

    if not refresh_token:
        raise credentials_exc

    # Find the user whose hash matches
    token_hash = hash_refresh_token(refresh_token)
    user: UserAuth | None = (
        db.query(UserAuth)
        .filter(UserAuth.refresh_token_hash == token_hash)
        .first()
    )

    if not user or not verify_refresh_token(refresh_token, user.refresh_token_hash):
        raise credentials_exc

    # Issue a new access token
    new_access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return RefreshResponse(access_token=new_access_token)


# ── POST /auth/logout ──────────────────────────────────────────────────────────
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    current_user: UserAuth = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Invalidate the current session.

    Nullifies the refresh_token_hash in the DB (so the cookie becomes useless)
    and instructs the browser to delete the cookie.
    """
    current_user.refresh_token_hash = None
    db.commit()
    _clear_refresh_cookie(response)


# ── POST /auth/change-password ─────────────────────────────────────────────────
@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    body: ChangePasswordRequest,
    current_user: UserAuth = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Change the authenticated user's password.

    - Verifies the current password before accepting the change.
    - Sets must_change_password to False after a successful change.
    - The caller must re-authenticate to get a new token reflecting the updated state.
    """
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    if body.new_password == body.current_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password.",
        )

    current_user.password_hash = hash_password(body.new_password)
    current_user.must_change_password = False
    db.commit()


# ── GET /auth/me ───────────────────────────────────────────────────────────────
@router.get("/me", response_model=UserAuthOut)
def get_me(current_user: UserAuth = Depends(get_current_user)) -> UserAuth:
    """
    Return the current authenticated user's profile.

    Used by the frontend to re-hydrate AuthContext after a page refresh
    (call /auth/refresh first to get a new access token, then /auth/me).
    """
    return current_user
