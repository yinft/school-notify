from fastapi import APIRouter, HTTPException, status

from app.schemas.device import DeviceListResponse, DeviceRegistrationRequest, DeviceResponse
from app.services.store import DeviceNotFoundError, store


router = APIRouter(prefix="/devices")


@router.get("")
def list_devices() -> DeviceListResponse:
    return DeviceListResponse(items=store.list_devices())


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_device(payload: DeviceRegistrationRequest) -> DeviceResponse:
    return store.register_device(
        device_id=payload.device_id,
        device_name=payload.device_name,
        client_version=payload.client_version,
    )


@router.post("/{device_id}/heartbeat")
def heartbeat_device(device_id: str) -> DeviceResponse:
    try:
        return store.heartbeat_device(device_id=device_id)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail="device not found") from exc
