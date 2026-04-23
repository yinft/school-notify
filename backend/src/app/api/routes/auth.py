from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps.auth import require_current_user, require_session_token
from app.db import get_db_session
from app.schemas.auth import AuthLoginRequest, AuthSessionResponse
from app.services.auth_sessions import create_auth_session, get_or_create_user_by_openid, revoke_session_by_token
from app.services.wechat_auth import build_session_token, exchange_code_for_session


router = APIRouter()


@router.post(
    "/login",
    summary="微信登录",
    description="【小程序端】使用微信小程序 wx.login() 获取的临时 code 换取会话令牌。成功返回 user_id 和 session_token。",
    responses={502: {"description": "微信登录失败"}},
)
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


@router.post(
    "/logout",
    summary="退出登录",
    description="【小程序端】注销当前会话令牌，令牌即刻失效。",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={204: {"description": "退出成功，无返回内容"}, 401: {"description": "无效或已过期的会话令牌"}},
)
def logout(session_token: str = Depends(require_session_token), db: Session = Depends(get_db_session)) -> Response:
    revoke_session_by_token(db, session_token=session_token)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/whoami",
    summary="查询当前用户",
    description="【小程序端】根据请求头中的会话令牌返回当前用户信息，用于校验令牌是否有效。",
    responses={401: {"description": "无效或已过期的会话令牌"}},
)
def whoami(current_user_id: str = Depends(require_current_user)) -> AuthSessionResponse:
    return build_auth_session(openid=current_user_id)


def build_auth_session(*, openid: str) -> AuthSessionResponse:
    return AuthSessionResponse(
        user_id=openid,
        session_token=build_session_token(openid),
        auth_provider="wechat",
    )
