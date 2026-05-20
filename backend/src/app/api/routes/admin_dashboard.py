from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps.admin_auth import require_current_admin
from app.core.db import get_db_session
from app.schemas.admin_dashboard import AdminDashboardNotificationTrendResponse, AdminDashboardSummaryResponse
from app.services.admin_dashboard import get_dashboard_summary, get_notification_trend


router = APIRouter()


@router.get("/summary", response_model=AdminDashboardSummaryResponse)
def summary(
    _: object = Depends(require_current_admin),
    db: Session = Depends(get_db_session),
    trend_days: int = Query(7, ge=7, le=30),
) -> AdminDashboardSummaryResponse:
    return AdminDashboardSummaryResponse(**get_dashboard_summary(db, trend_days=trend_days))


@router.get("/notification-trend", response_model=AdminDashboardNotificationTrendResponse)
def notification_trend(
    _: object = Depends(require_current_admin),
    db: Session = Depends(get_db_session),
    days: int = Query(7, ge=7, le=30),
) -> AdminDashboardNotificationTrendResponse:
    return AdminDashboardNotificationTrendResponse(items=get_notification_trend(db, days=days))
