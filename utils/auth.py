"""User authentication for POLLY — bcrypt passwords, user CRUD against polly.users."""
import logging
from typing import Optional, Dict

import bcrypt as _bcrypt

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return _bcrypt.checkpw(password.encode(), password_hash.encode())


# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------

def _get_pool():
    from utils.db_pool import DatabasePool
    return DatabasePool.get()


def create_user(email: str, password: str, display_name: Optional[str] = None) -> Optional[Dict]:
    """Create a new user. Returns user dict or None if email already exists."""
    from sqlalchemy import text

    pw_hash = hash_password(password)
    pool = _get_pool()
    with pool.get_session() as session:
        result = session.execute(
            text("""
                INSERT INTO polly.users (email, password_hash, full_name)
                VALUES (:email, :pw_hash, :name)
                ON CONFLICT (email) DO NOTHING
                RETURNING id, email, full_name, persona, is_active, created_at
            """),
            {
                "email": email.lower().strip(),
                "pw_hash": pw_hash,
                "name": display_name or email.split("@")[0],
            },
        )
        row = result.fetchone()
        if not row:
            return None
        return dict(zip(result.keys(), row))


def get_user_by_email(email: str) -> Optional[Dict]:
    from sqlalchemy import text
    pool = _get_pool()
    with pool.get_session() as session:
        result = session.execute(
            text("""
                SELECT id, email, password_hash, full_name, persona, is_active, created_at
                FROM polly.users
                WHERE email = :email AND is_active = TRUE
            """),
            {"email": email.lower().strip()},
        )
        row = result.fetchone()
        if not row:
            return None
        return dict(zip(result.keys(), row))


def authenticate(email: str, password: str) -> Optional[Dict]:
    """Authenticate by email + password. Returns user dict on success, None on failure."""
    user = get_user_by_email(email)
    if not user:
        return None
    pw_hash = user.get("password_hash")
    if not pw_hash:
        return None
    if not verify_password(password, pw_hash):
        return None
    user.pop("password_hash", None)
    return user
