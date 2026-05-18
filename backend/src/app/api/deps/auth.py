from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.services.auth_sessions import get_active_session_by_token, get_cached_auth_user_id, refresh_cached_auth_session
from app.services.wechat_auth import WeChatLoginError, parse_session_token

_bearer_scheme = HTTPBearer(auto_error=False)


def require_session_token(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db_session),
) -> str:
    if credentials is None:
        raise HTTPException(status_code=401, detail="not authenticated")
    token = credentials.credentials
    try:
        parsed_user_id = parse_session_token(token)
    except WeChatLoginError as exc:
        raise HTTPException(status_code=401, detail="invalid session token") from exc

    cached_user_id = get_cached_auth_user_id(token)
    if cached_user_id and cached_user_id == parsed_user_id:
        refresh_cached_auth_session(session_token=token, user_id=cached_user_id)
        return token

    active_session = get_active_session_by_token(db, session_token=token)
    if not active_session or active_session.user.user_id != parsed_user_id:
        raise HTTPException(status_code=401, detail="invalid session token")

    refresh_cached_auth_session(session_token=token, user_id=active_session.user.user_id)

    return token


def require_current_user(session_token: str = Depends(require_session_token), db: Session = Depends(get_db_session)) -> str:
    cached_user_id = get_cached_auth_user_id(session_token)
    if cached_user_id:
        refresh_cached_auth_session(session_token=session_token, user_id=cached_user_id)
        return cached_user_id

    active_session = get_active_session_by_token(db, session_token=session_token)
    if not active_session:
        raise HTTPException(status_code=401, detail="invalid session token")
    return active_session.user.user_id


def ensure_same_user(*, expected_user_id: str, current_user_id: str) -> None:
    if expected_user_id != current_user_id:
        raise HTTPException(status_code=403, detail="forbidden")


def require_device_token(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> str:
    if credentials is None:
        raise HTTPException(status_code=401, detail="not authenticated")
    token = credentials.credentials
    if not token.startswith("device-token:"):
        raise HTTPException(status_code=401, detail="invalid device token")
    try:
        parsed_device_id = parse_session_token(token)
    except WeChatLoginError as exc:
        raise HTTPException(status_code=401, detail="invalid device token") from exc
    return parsed_device_id
