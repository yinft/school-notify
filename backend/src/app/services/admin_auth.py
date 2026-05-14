from datetime import datetime
import hashlib
import hmac
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models import AdminSession, AdminUser


def _hash_password(password: str, *, salt: str | None = None) -> str:
    password_salt = salt or secrets.token_hex(16)
    derived_key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=password_salt.encode("utf-8"),
        n=2**14,
        r=8,
        p=1,
        dklen=32,
    )
    return f"scrypt${password_salt}${derived_key.hex()}"


def _verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith("legacy-plain$"):
        return password_hash == f"legacy-plain${password}"
    if password_hash.startswith("plain$"):
        return password_hash == f"plain${password}"
    if not password_hash.startswith("scrypt$"):
        return False

    _, salt, expected_hash = password_hash.split("$", 2)
    actual_hash = _hash_password(password, salt=salt).split("$", 2)[2]
    return hmac.compare_digest(actual_hash, expected_hash)


def _needs_password_upgrade(password_hash: str) -> bool:
    return password_hash.startswith("legacy-plain$") or password_hash.startswith("plain$")


def build_admin_session_token(username: str) -> str:
    signature = hmac.new(
        settings.session_signing_secret.encode("utf-8"),
        f"admin:{username}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"admin-session:{username}:{signature}"


def parse_admin_session_token(token: str) -> str:
    prefix = "admin-session:"
    if not token.startswith(prefix):
        raise ValueError("invalid admin session")
    remainder = token.removeprefix(prefix).strip()
    username, sep, signature = remainder.partition(":")
    if not username or not sep or not signature:
        raise ValueError("invalid admin session")
    expected_signature = build_admin_session_token(username).rsplit(":", 1)[-1]
    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError("invalid admin session")
    return username


def verify_admin_credentials(db: Session, *, username: str, password: str) -> AdminUser | None:
    admin = db.execute(select(AdminUser).where(AdminUser.username == username, AdminUser.is_active.is_(True))).scalar_one_or_none()
    if admin is None:
        return None
    if not _verify_password(password, admin.password_hash):
        return None
    if _needs_password_upgrade(admin.password_hash):
        admin.password_hash = _hash_password(password)
    admin.last_login_at = datetime.now()
    return admin


def ensure_admin_user(db: Session, *, username: str, password: str, display_name: str) -> AdminUser:
    admin = db.execute(select(AdminUser).where(AdminUser.username == username)).scalar_one_or_none()
    if admin is not None:
        return admin

    admin = AdminUser(
        username=username,
        password_hash=_hash_password(password),
        display_name=display_name,
        is_active=True,
    )
    db.add(admin)
    db.flush()
    return admin


def create_admin_session(db: Session, *, admin_user: AdminUser) -> str:
    token = build_admin_session_token(admin_user.username)
    existing = db.execute(select(AdminSession).where(AdminSession.session_token == token)).scalar_one_or_none()
    if existing:
        existing.admin_user_id = admin_user.id
        existing.revoked_at = None
        return token
    db.add(AdminSession(admin_user_id=admin_user.id, session_token=token))
    return token


def get_active_admin_by_token(db: Session, *, session_token: str) -> AdminUser | None:
    username = parse_admin_session_token(session_token)
    session = db.execute(
        select(AdminSession).where(AdminSession.session_token == session_token, AdminSession.revoked_at.is_(None))
    ).scalar_one_or_none()
    if session is None:
        return None
    return db.execute(select(AdminUser).where(AdminUser.id == session.admin_user_id, AdminUser.username == username)).scalar_one_or_none()


def revoke_admin_session(db: Session, *, session_token: str) -> None:
    session = db.execute(select(AdminSession).where(AdminSession.session_token == session_token)).scalar_one_or_none()
    if session and session.revoked_at is None:
        session.revoked_at = datetime.now()
