from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps.auth import ensure_same_user, require_current_user
from app.schemas.notification import NotificationCreateRequest, NotificationCreateResponse, NotificationRecordListResponse
from app.services.device_connections import device_connections
from app.services.store import DeviceNotBoundError, DeviceNotFoundError, DeviceOfflineError, store


router = APIRouter(prefix="/notifications")


@router.get("")
def list_notifications(
    sender_user_id: str,
    limit: int = 20,
    offset: int = 0,
    current_user_id: str = Depends(require_current_user),
) -> NotificationRecordListResponse:
    ensure_same_user(expected_user_id=sender_user_id, current_user_id=current_user_id)
    items, total = store.list_notifications_for_user(sender_user_id=sender_user_id, limit=limit, offset=offset)
    return NotificationRecordListResponse(items=items, total=total)


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_notification(payload: NotificationCreateRequest, current_user_id: str = Depends(require_current_user)) -> NotificationCreateResponse:
    ensure_same_user(expected_user_id=payload.sender_user_id, current_user_id=current_user_id)
    try:
        response, deliveries = store.create_notification(
            sender_user_id=payload.sender_user_id,
            title=payload.title,
            content=payload.content,
            level=payload.level,
            device_ids=payload.device_ids,
        )
        await device_connections.send_notifications(deliveries=deliveries)
        return response
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail="device not found") from exc
    except DeviceNotBoundError as exc:
        raise HTTPException(status_code=403, detail="device not bound to user") from exc
    except DeviceOfflineError as exc:
        raise HTTPException(status_code=409, detail="device offline") from exc
