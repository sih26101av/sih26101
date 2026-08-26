"""
auth/seed.py
─────────────────────────────────────────────────────────────────────────────
One-shot database seeding script.

Run from inside the main-lms-backend directory:
    python -m auth.seed
  or
    python auth/seed.py

What it does
────────────
1. Creates the users_auth table if it doesn't exist.
2. Fetches all 151 MoSPI officials from the Mock iGOT Server at:
       GET http://localhost:8001/api/admin/v1/users
   The mock server must be running before you execute this script.
3. For each official, derives a default password:
       lowercase(firstName) + last 2 digits of the numeric userId suffix
   Example: userId="usr_720465595", firstName="Gabriel" → password "gabriel95"
4. Bcrypt-hashes every password and inserts a UserAuth row with:
       role="learner", must_change_password=True
5. Inserts one hardcoded admin:
       username="admin", password="admin123" (hashed), role="admin",
       must_change_password=False
6. Skips rows that already exist (idempotent — safe to re-run).

Prints a summary at the end.
"""

import os
import sys

# ── Allow running as a script from the backend root ───────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from auth.database import AuthBase, SessionLocal, engine
from auth.models import UserAuth
from auth.security import hash_password

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────────
IGOT_BASE_URL: str = os.getenv("IGOT_MOCK_BASE_URL", "http://localhost:8001")
IGOT_TOKEN: str = os.getenv("IGOT_MOCK_TOKEN", "mock-api-key-2026")
ADMIN_USERNAME: str = "admin"
ADMIN_PASSWORD: str = "admin123"


def _derive_password(first_name: str, user_id: str) -> str:
    """
    Default password = lowercase(firstName) + last 2 digits of the numeric userId suffix.

    userId format: "usr_XXXXXXXXX"
    The numeric suffix is the part after "usr_".
    Last 2 digits = [-2:] of that numeric string.

    Example: "Gabriel", "usr_720465595" → "gabriel95"
    """
    numeric_suffix = user_id.replace("usr_", "").replace("usr", "")
    last_two = numeric_suffix[-2:] if len(numeric_suffix) >= 2 else numeric_suffix
    return first_name.lower() + last_two


def _fetch_officials() -> list[dict]:
    """Call the mock iGOT server's admin roster endpoint."""
    url = f"{IGOT_BASE_URL}/api/admin/v1/users"
    headers = {"x-authenticated-user-token": IGOT_TOKEN}

    print(f"[seed] Fetching officials from {url} …")
    try:
        resp = httpx.get(url, headers=headers, timeout=15.0)
        resp.raise_for_status()
    except httpx.ConnectError:
        print(
            f"\n[seed] ERROR: Could not connect to the Mock iGOT Server at {IGOT_BASE_URL}.\n"
            "       Please start it first:  python mock_igot_server.py\n"
            "       (from the mock-igot-server directory)\n"
        )
        sys.exit(1)
    except httpx.HTTPStatusError as exc:
        print(f"[seed] ERROR: HTTP {exc.response.status_code} from mock server.")
        sys.exit(1)

    data = resp.json()
    users = data.get("result", {}).get("users", [])
    print(f"[seed] Received {len(users)} users from mock server.")
    return users


def _seed_officials(db: Session, officials: list[dict]) -> tuple[int, int]:
    """Insert learner rows. Returns (inserted, skipped)."""
    inserted = 0
    skipped = 0

    for official in officials:
        user_id: str = official.get("userId", "")
        first_name: str = official.get("firstName", "user")

        if not user_id:
            skipped += 1
            continue

        # Idempotency check
        existing = db.query(UserAuth).filter(UserAuth.username == user_id).first()
        if existing:
            skipped += 1
            continue

        password = _derive_password(first_name, user_id)
        row = UserAuth(
            username=user_id,
            password_hash=hash_password(password),
            role="learner",
            must_change_password=True,
            refresh_token_hash=None,
        )
        db.add(row)
        inserted += 1

    db.commit()
    return inserted, skipped


def _seed_admin(db: Session) -> bool:
    """Insert the hardcoded admin user. Returns True if inserted, False if already exists."""
    existing = db.query(UserAuth).filter(UserAuth.username == ADMIN_USERNAME).first()
    if existing:
        return False

    admin = UserAuth(
        username=ADMIN_USERNAME,
        password_hash=hash_password(ADMIN_PASSWORD),
        role="admin",
        must_change_password=False,
        refresh_token_hash=None,
    )
    db.add(admin)
    db.commit()
    return True


def main() -> None:
    # 1. Ensure table exists
    print("[seed] Creating users_auth table if not exists …")
    AuthBase.metadata.create_all(bind=engine)

    # 2. Fetch officials from mock server
    officials = _fetch_officials()

    # 3. Open a DB session and seed
    db: Session = SessionLocal()
    try:
        inserted, skipped = _seed_officials(db, officials)
        admin_created = _seed_admin(db)
    finally:
        db.close()

    # 4. Print summary
    print("\n" + "=" * 60)
    print("  Seed Complete")
    print("=" * 60)
    print(f"  Officials inserted : {inserted}")
    print(f"  Officials skipped  : {skipped} (already existed)")
    print(f"  Admin user         : {'CREATED (admin / admin123)' if admin_created else 'already existed'}")
    print("=" * 60)
    print("\n  Default password formula: lowercase(firstName) + last 2 digits of userId")
    print("  Example: Gabriel / usr_720465595 → password: gabriel95")
    print("\n  All seeded learners have must_change_password=True.\n")


if __name__ == "__main__":
    main()
