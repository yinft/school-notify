from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps.auth import ensure_same_user, require_current_user, require_device_token
from app.schemas.binding import (
    BindingCodeCreateRequest,
    BindingCodeResponse,
    BindingCreateRequest,
    BindingDevicePreviewResponse,
    BindingResponse,
)
from app.services.store import BindingCodeNotFoundError, DeviceNotBoundError, DeviceNotFoundError, store


router = APIRouter(prefix="/bindings")


@router.post(
    "/code",
    summary="生成绑定码",
    description="【设备端】为指定设备生成一次性绑定码。用户在小程序中输入此绑定码完成设备绑定。",
    responses={404: {"description": "设备不存在"}},
)
def create_binding_code(payload: BindingCodeCreateRequest, parsed_device_id: str = Depends(require_device_token)) -> BindingCodeResponse:
    if parsed_device_id != payload.device_id:
        raise HTTPException(status_code=403, detail="forbidden")
    try:
        return store.create_binding_code(device_id=payload.device_id)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail="device not found") from exc


@router.get(
    "/code/{code}/device",
    summary="查询绑定码对应设备",
    description="【小程序端】根据绑定码预览待绑定设备信息，用于在绑定前确认并补全名称、位置。",
    responses={401: {"description": "未认证"}, 404: {"description": "绑定码不存在或已过期"}},
)
def get_binding_code_device(code: str, _: str = Depends(require_current_user)) -> BindingDevicePreviewResponse:
    try:
        return store.get_device_by_binding_code(code=code)
    except BindingCodeNotFoundError as exc:
        raise HTTPException(status_code=404, detail="binding code not found") from exc


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="绑定设备",
    description="【小程序端】用户在小程序中输入绑定码，将设备绑定到自己的账号。绑定码验证通过后即失效。",
    responses={
        201: {"description": "绑定成功"},
        401: {"description": "未认证"},
        403: {"description": "无权绑定到其他用户"},
        404: {"description": "绑定码不存在或已过期"},
    },
)
def create_binding(payload: BindingCreateRequest, current_user_id: str = Depends(require_current_user)) -> BindingResponse:
    ensure_same_user(expected_user_id=payload.user_id, current_user_id=current_user_id)
    try:
        return store.bind_user_to_device(
            user_id=payload.user_id,
            code=payload.code,
            device_name=payload.device_name,
            location_label=payload.location_label,
        )
    except BindingCodeNotFoundError as exc:
        raise HTTPException(status_code=404, detail="binding code not found") from exc


@router.delete(
    "/{device_id}",
    summary="解绑设备",
    description="【小程序端】解绑当前用户和指定设备的关系，不影响设备本身注册和其他用户绑定。",
    responses={
        200: {"description": "解绑成功"},
        401: {"description": "未认证"},
        403: {"description": "无权解绑其他用户设备"},
        404: {"description": "设备不存在或当前用户未绑定该设备"},
    },
)
def delete_binding(device_id: str, user_id: str, current_user_id: str = Depends(require_current_user)) -> BindingResponse:
    ensure_same_user(expected_user_id=user_id, current_user_id=current_user_id)
    try:
        return store.unbind_user_from_device(user_id=user_id, device_id=device_id)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail="device not found") from exc
    except DeviceNotBoundError as exc:
        raise HTTPException(status_code=404, detail="device not bound to user") from exc
