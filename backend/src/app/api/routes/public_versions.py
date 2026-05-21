from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.schemas.admin_version import PublicVersionListResponse, PublicVersionResponse
from app.services.admin_versions import list_public_versions


router = APIRouter()


def _to_response(version) -> PublicVersionResponse:
    return PublicVersionResponse(
        platform=version.platform,
        version=version.version,
        release_notes=version.release_notes,
        download_url=version.download_url,
        file_size=version.file_size,
        published_at=version.published_at,
    )


@router.get("", response_model=PublicVersionListResponse)
def list_items(platform: str | None = Query(default=None), db: Session = Depends(get_db_session)) -> PublicVersionListResponse:
    return PublicVersionListResponse(items=[_to_response(item) for item in list_public_versions(db, platform=platform)])
