from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps.admin_auth import require_current_admin
from app.core.db import get_db_session
from app.schemas.admin_user import AdminUserDetailResponse, AdminUserDeviceSummary, AdminUserListItem, AdminUserListResponse, AdminUserNotificationSummary
from app.services.admin_queries import get_admin_user_detail, list_admin_users, paginate_items


router = APIRouter()


@router.get("", response_model=AdminUserListResponse)
def list_items(
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _: object = Depends(require_current_admin),
    db: Session = Depends(get_db_session),
) -> AdminUserListResponse:
    sliced, total = paginate_items(list_admin_users(db, keyword=keyword), page=page, page_size=page_size)
    return AdminUserListResponse(
        items=[AdminUserListItem(**item) for item in sliced],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{user_id}", response_model=AdminUserDetailResponse)
def detail(user_id: str, _: object = Depends(require_current_admin), db: Session = Depends(get_db_session)) -> AdminUserDetailResponse:
    item = get_admin_user_detail(db, user_id=user_id)
    if item is None:
        raise HTTPException(status_code=404, detail="user not found")
    return AdminUserDetailResponse(
        user_id=item["user_id"],
        nickname=item["nickname"],
        avatar_url=item["avatar_url"],
        devices=[AdminUserDeviceSummary(**entry) for entry in item["devices"]],
        recent_notifications=[AdminUserNotificationSummary(**entry) for entry in item["recent_notifications"]],
    )
