from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.services.admin_auth import get_active_admin_by_token, parse_admin_session_token

_bearer_scheme = HTTPBearer(auto_error=False)


def require_admin_session_token(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db_session),
) -> str:
    if credentials is None:
        raise HTTPException(status_code=401, detail="not authenticated")
    token = credentials.credentials
    try:
        parse_admin_session_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="invalid admin session") from exc
    if get_active_admin_by_token(db, session_token=token) is None:
        raise HTTPException(status_code=401, detail="invalid admin session")
    return token


def require_current_admin(session_token: str = Depends(require_admin_session_token), db: Session = Depends(get_db_session)):
    admin = get_active_admin_by_token(db, session_token=session_token)
    if admin is None:
        raise HTTPException(status_code=401, detail="invalid admin session")
    return admin
