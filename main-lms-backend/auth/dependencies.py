"""
auth/dependencies.py
─────────────────────────────────────────────────────────────────────────────
FastAPI dependency functions that enforce authentication and authorisation.

Usage in route functions:
    @router.get("/protected")
    def my_route(user: UserAuth = Depends(get_current_user)):
        ...

    @router.get("/admin-only")
    def admin_route(user: UserAuth = Depends(require_role("admin"))):
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import UserAuth
from .security import decode_access_token

# ── OAuth2 scheme ──────────────────────────────────────────────────────────────
# tokenUrl must match the login endpoint we register on the main app
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── get_current_user ───────────────────────────────────────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserAuth:
    """
    Decodes the Bearer JWT, looks up the user in auth.db.
    Raises HTTP 401 for any token problem or missing user.
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exc
    except ValueError:
        raise credentials_exc

    user = db.query(UserAuth).filter(UserAuth.username == username).first()
    if user is None:
        raise credentials_exc

    return user


# ── require_role ───────────────────────────────────────────────────────────────
def require_role(*roles: str):
    """
    Returns a FastAPI dependency that checks the current user's role.

    Example:
        Depends(require_role("admin"))
        Depends(require_role("admin", "trainer"))
    """
    def _checker(current_user: UserAuth = Depends(get_current_user)) -> UserAuth:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(roles)}. "
                       f"Your role: {current_user.role}",
            )
        return current_user

    return _checker
