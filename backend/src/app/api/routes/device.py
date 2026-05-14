from fastapi import APIRouter, Header, HTTPException, status

from app.api.deps.auth import require_device_token_for_device
from app.schemas.device import DeviceListResponse, DeviceRegistrationRequest, DeviceResponse, HeartbeatResponse
from app.services.store import DeviceNotFoundError, store


router = APIRouter(prefix="/devices")


@router.get(
    "",
    summary="获取设备列表",
    description="【通用】返回所有已注册设备的列表。",
)
def list_devices() -> DeviceListResponse:
    return DeviceListResponse(items=store.list_devices())


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="注册设备",
    description="【设备端】设备首次启动时调用，向服务端注册自身信息并获取 device_token，用于后续 WebSocket 连接鉴权。",
)
def register_device(payload: DeviceRegistrationRequest) -> DeviceResponse:
    return store.register_device(
        device_id=payload.device_id,
        device_name=payload.device_name,
        client_version=payload.client_version,
    )


@router.post(
    "/{device_id}/heartbeat",
    summary="设备心跳",
    description="【设备端】设备定期上报心跳以维持在线状态。服务端更新 last_seen_at 时间戳。",
    responses={404: {"description": "设备不存在"}},
)
def heartbeat_device(device_id: str, authorization: str = Header(default="")) -> HeartbeatResponse:
    require_device_token_for_device(expected_device_id=device_id, authorization=authorization)
    try:
        return store.heartbeat_device(device_id=device_id)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail="device not found") from exc
