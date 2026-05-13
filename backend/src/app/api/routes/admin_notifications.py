from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps.admin_auth import require_current_admin
from app.core.db import get_db_session
from app.schemas.admin_notification import AdminNotificationDeliveryItem, AdminNotificationDetailResponse, AdminNotificationListItem, AdminNotificationListResponse
from app.services.admin_queries import get_admin_notification_detail, list_admin_notifications, paginate_items


router = APIRouter()


@router.get("", response_model=AdminNotificationListResponse)
def list_items(
    keyword: str | None = Query(default=None),
    sender_user_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _: object = Depends(require_current_admin),
    db: Session = Depends(get_db_session),
) -> AdminNotificationListResponse:
    sliced, total = paginate_items(list_admin_notifications(db, keyword=keyword, sender_user_id=sender_user_id), page=page, page_size=page_size)
    return AdminNotificationListResponse(
        items=[AdminNotificationListItem(**item) for item in sliced],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{notification_id}", response_model=AdminNotificationDetailResponse)
def detail(notification_id: str, _: object = Depends(require_current_admin), db: Session = Depends(get_db_session)) -> AdminNotificationDetailResponse:
    item = get_admin_notification_detail(db, notification_id=notification_id)
    if item is None:
        raise HTTPException(status_code=404, detail="notification not found")
    return AdminNotificationDetailResponse(
        notification_id=item["notification_id"],
        sender_user_id=item["sender_user_id"],
        title=item["title"],
        content=item["content"],
        created_at=item["created_at"],
        deliveries=[AdminNotificationDeliveryItem(**entry) for entry in item["deliveries"]],
    )
