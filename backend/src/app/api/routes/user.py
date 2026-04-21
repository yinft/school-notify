from fastapi import APIRouter

from app.schemas.device import DeviceListResponse
from app.services.store import store


router = APIRouter(prefix="/users")


@router.get("/{user_id}/devices")
def list_user_devices(user_id: str) -> DeviceListResponse:
    return DeviceListResponse(items=store.list_devices_for_user(user_id=user_id))
