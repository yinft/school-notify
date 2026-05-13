from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.admin_auth import require_current_admin
from app.core.db import get_db_session
from app.schemas.admin_dashboard import AdminDashboardSummaryResponse
from app.services.admin_dashboard import get_dashboard_summary


router = APIRouter()


@router.get("/summary", response_model=AdminDashboardSummaryResponse)
def summary(_: object = Depends(require_current_admin), db: Session = Depends(get_db_session)) -> AdminDashboardSummaryResponse:
    return AdminDashboardSummaryResponse(**get_dashboard_summary(db))
