from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import AuthSession, User
from app.services.redis_service import redis_service
from app.core.settings import settings


def get_or_create_user_by_openid(db: Session, *, openid: str) -> User:
    user = db.execute(select(User).where(User.openid == openid)).scalar_one_or_none()
    if user:
        return user

    user = User(user_id=openid, openid=openid)
    db.add(user)
    db.flush()
    return user


def create_auth_session(db: Session, *, user: User, session_token: str) -> AuthSession:
    existing = db.execute(select(AuthSession).where(AuthSession.session_token == session_token)).scalar_one_or_none()
    if existing:
        existing.user_id = user.id
        existing.revoked_at = None
        db.flush()
        _cache_session(session_token=session_token, user_id=user.user_id)
        return existing

    session = AuthSession(user_id=user.id, session_token=session_token)
    db.add(session)
    db.flush()
    _cache_session(session_token=session_token, user_id=user.user_id)
    return session


def get_active_session_by_token(db: Session, *, session_token: str) -> AuthSession | None:
    return db.execute(
        select(AuthSession)
        .options(joinedload(AuthSession.user))
        .where(AuthSession.session_token == session_token, AuthSession.revoked_at.is_(None))
    ).scalar_one_or_none()


def revoke_session_by_token(db: Session, *, session_token: str) -> None:
    session = db.execute(select(AuthSession).where(AuthSession.session_token == session_token)).scalar_one_or_none()
    if session and session.revoked_at is None:
        session.revoked_at = datetime.now(UTC)
        db.flush()
    redis_service.revoke_cached_auth_session(session_token)


def get_cached_auth_user_id(session_token: str) -> str | None:
    return redis_service.get_cached_auth_user(session_token)


def refresh_cached_auth_session(*, session_token: str, user_id: str) -> None:
    _cache_session(session_token=session_token, user_id=user_id)


def _cache_session(*, session_token: str, user_id: str) -> None:
    redis_service.cache_auth_session(
        session_token=session_token,
        user_id=user_id,
        ttl_seconds=settings.auth_session_cache_ttl_seconds,
    )
