from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps.auth import require_current_user
from app.core.db import SessionLocal, get_db_session
from app.models import User
from app.schemas.auth import UserProfileResponse, UserProfileUpdateRequest
from app.schemas.device import DeviceListResponse, DeviceResponse, DeviceUpdateRequest
from app.services.store import DeviceNotBoundError, DeviceNotFoundError, store


router = APIRouter(prefix="/users")


@router.get(
    "/{user_id}/devices",
    summary="获取用户绑定的设备列表",
    description="【小程序端】查询指定用户绑定的所有设备信息。只能查询自己的设备。",
    responses={403: {"description": "无权查看其他用户的设备"}, 401: {"description": "未认证"}},
)
def list_user_devices(user_id: str, current_user_id: str = Depends(require_current_user)) -> DeviceListResponse:
    from app.api.deps.auth import ensure_same_user
    ensure_same_user(expected_user_id=user_id, current_user_id=current_user_id)
    return DeviceListResponse(items=store.list_devices_for_user(user_id=user_id))


@router.patch(
    "/{user_id}/devices/{device_id}",
    summary="更新用户绑定设备信息",
    description="【小程序端】修改已绑定设备的显示名称和位置。只能修改自己的设备。",
    responses={403: {"description": "无权修改该设备"}, 404: {"description": "设备不存在"}},
)
def update_user_device(
    user_id: str,
    device_id: str,
    payload: DeviceUpdateRequest,
    current_user_id: str = Depends(require_current_user),
) -> DeviceResponse:
    from app.api.deps.auth import ensure_same_user
    ensure_same_user(expected_user_id=user_id, current_user_id=current_user_id)
    try:
        return store.update_bound_device(
            user_id=user_id,
            device_id=device_id,
            device_name=payload.device_name,
            location_label=payload.location_label,
        )
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail="device not found") from exc
    except DeviceNotBoundError as exc:
        raise HTTPException(status_code=403, detail="device not bound to user") from exc


@router.patch(
    "/me",
    summary="更新当前用户资料",
    description="【小程序端】更新当前登录用户的昵称和头像。仅传入的字段会被更新。",
    responses={401: {"description": "未认证"}, 404: {"description": "用户不存在"}},
)
def update_profile(
    payload: UserProfileUpdateRequest,
    current_user_id: str = Depends(require_current_user),
) -> UserProfileResponse:
    with SessionLocal() as session:
        user = session.execute(select(User).where(User.user_id == current_user_id)).scalar_one_or_none()
        if user is None:
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
