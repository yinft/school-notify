from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps.auth import require_current_user, require_session_token
from app.db import get_db_session
from app.schemas.auth import AuthLoginRequest, AuthSessionResponse
from app.services.auth_sessions import create_auth_session, get_or_create_user_by_openid, revoke_session_by_token
from app.services.wechat_auth import build_session_token, exchange_code_for_session


router = APIRouter()


@router.post("/login")
def login(payload: AuthLoginRequest, db: Session = Depends(get_db_session)) -> AuthSessionResponse:
    try:
        session = exchange_code_for_session(payload.code)
        openid = session["openid"]
    except Exception as exc:
        raise HTTPException(status_code=502, detail="wechat login failed") from exc

    auth_session = build_auth_session(openid=openid)
    user = get_or_create_user_by_openid(db, openid=openid)
    create_auth_session(db, user=user, session_token=auth_session.session_token)
    db.commit()
    return auth_session


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(session_token: str = Depends(require_session_token), db: Session = Depends(get_db_session)) -> Response:
    revoke_session_by_token(db, session_token=session_token)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/whoami")
def whoami(current_user_id: str = Depends(require_current_user)) -> AuthSessionResponse:
    return build_auth_session(openid=current_user_id)


def build_auth_session(*, openid: str) -> AuthSessionResponse:
    return AuthSessionResponse(
        user_id=openid,
        session_token=build_session_token(openid),
        auth_provider="wechat",
    )
