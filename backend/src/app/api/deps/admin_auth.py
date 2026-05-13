from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.services.admin_auth import get_active_admin_by_token, parse_admin_session_token


def require_admin_session_token(authorization: str = Header(default=""), db: Session = Depends(get_db_session)) -> str:
    token = authorization.removeprefix("Bearer ").strip()
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
