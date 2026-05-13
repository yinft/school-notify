from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.schemas.admin_version import PublicVersionListResponse, PublicVersionResponse
from app.services.admin_versions import get_recommended_public_version, list_public_versions


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


@router.get("/recommended", response_model=PublicVersionResponse)
def recommended(platform: str = Query(...), db: Session = Depends(get_db_session)) -> PublicVersionResponse:
    version = get_recommended_public_version(db, platform=platform)
    if version is None:
        raise HTTPException(status_code=404, detail="recommended version not found")
    return _to_response(version)
