from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps.admin_auth import require_current_admin
from app.core.db import get_db_session
from app.schemas.admin_device import AdminDeviceDetailResponse, AdminDeviceListResponse, AdminDeviceListItem, AdminDeviceNotificationSummary, AdminDeviceUpdateRequest, AdminDeviceUserSummary
from app.services.admin_queries import get_admin_device_detail, list_admin_devices, paginate_items, unbind_admin_device_user, update_admin_device


router = APIRouter()


@router.get("", response_model=AdminDeviceListResponse)
def list_items(
    keyword: str | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _: object = Depends(require_current_admin),
    db: Session = Depends(get_db_session),
) -> AdminDeviceListResponse:
    sliced, total = paginate_items(list_admin_devices(db, keyword=keyword, status=status), page=page, page_size=page_size)
    return AdminDeviceListResponse(
        items=[AdminDeviceListItem(**item) for item in sliced],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{device_id}", response_model=AdminDeviceDetailResponse)
def detail(device_id: str, _: object = Depends(require_current_admin), db: Session = Depends(get_db_session)) -> AdminDeviceDetailResponse:
    item = get_admin_device_detail(db, device_id=device_id)
    if item is None:
        raise HTTPException(status_code=404, detail="device not found")
    return AdminDeviceDetailResponse(
        device_id=item["device_id"],
        device_name=item["device_name"],
        location_label=item["location_label"],
        client_version=item["client_version"],
        status=item["status"],
        bound_users=[AdminDeviceUserSummary(**entry) for entry in item["bound_users"]],
        recent_notifications=[AdminDeviceNotificationSummary(**entry) for entry in item["recent_notifications"]],
    )


@router.patch("/{device_id}", response_model=AdminDeviceListItem)
def update(device_id: str, payload: AdminDeviceUpdateRequest, _: object = Depends(require_current_admin), db: Session = Depends(get_db_session)) -> AdminDeviceListItem:
    device = update_admin_device(db, device_id=device_id, device_name=payload.device_name, location_label=payload.location_label)
    if device is None:
        raise HTTPException(status_code=404, detail="device not found")
    db.commit()
    return AdminDeviceListItem(
        device_id=device.device_id,
        device_name=device.device_name,
        location_label=device.location_label,
        client_version=device.client_version,
        status=device.status,
        bound_users_count=0,
    )


@router.delete("/{device_id}/bindings/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def unbind(device_id: str, user_id: str, _: object = Depends(require_current_admin), db: Session = Depends(get_db_session)) -> Response:
    if not unbind_admin_device_user(db, device_id=device_id, user_id=user_id):
        raise HTTPException(status_code=404, detail="binding not found")
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
