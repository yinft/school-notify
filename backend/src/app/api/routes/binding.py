from fastapi import APIRouter, HTTPException, status

from app.schemas.binding import (
    BindingCodeCreateRequest,
    BindingCodeResponse,
    BindingCreateRequest,
    BindingResponse,
)
from app.services.store import BindingCodeNotFoundError, DeviceNotFoundError, store


router = APIRouter(prefix="/bindings")


@router.post("/code")
def create_binding_code(payload: BindingCodeCreateRequest) -> BindingCodeResponse:
    try:
        return store.create_binding_code(device_id=payload.device_id)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail="device not found") from exc


@router.post("", status_code=status.HTTP_201_CREATED)
def create_binding(payload: BindingCreateRequest) -> BindingResponse:
    try:
        return store.bind_user_to_device(user_id=payload.user_id, code=payload.code)
    except BindingCodeNotFoundError as exc:
        raise HTTPException(status_code=404, detail="binding code not found") from exc
