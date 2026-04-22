from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps.auth import require_current_user
from app.db import SessionLocal, get_db_session
from app.models import User
from app.schemas.auth import UserProfileResponse, UserProfileUpdateRequest
from app.schemas.device import DeviceListResponse
from app.services.store import store


router = APIRouter(prefix="/users")


@router.get("/{user_id}/devices")
def list_user_devices(user_id: str, current_user_id: str = Depends(require_current_user)) -> DeviceListResponse:
    from app.api.deps.auth import ensure_same_user
    ensure_same_user(expected_user_id=user_id, current_user_id=current_user_id)
    return DeviceListResponse(items=store.list_devices_for_user(user_id=user_id))


@router.patch("/me")
def update_profile(
    payload: UserProfileUpdateRequest,
    current_user_id: str = Depends(require_current_user),
) -> UserProfileResponse:
    with SessionLocal() as session:
        user = session.execute(select(User).where(User.user_id == current_user_id)).scalar_one_or_none()
        if user is None:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="user not found")
        if payload.nickname is not None:
            user.nickname = payload.nickname
        if payload.avatar_url is not None:
            user.avatar_url = payload.avatar_url
        session.commit()
        session.refresh(user)
        return UserProfileResponse(
            user_id=user.user_id,
            nickname=user.nickname,
            avatar_url=user.avatar_url,
        )
