from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps.admin_auth import require_current_admin
from app.core.db import get_db_session
from app.schemas.admin_version import AdminVersionCreateRequest, AdminVersionListResponse, AdminVersionResponse, AdminVersionUpdateRequest
from app.services.admin_versions import PublishedVersionDeleteError, create_version, delete_version, get_version, list_versions, publish_version, recommend_version, unpublish_version, update_version
from app.services.admin_queries import paginate_items


router = APIRouter()


def _to_response(version) -> AdminVersionResponse:
    return AdminVersionResponse(
        id=version.id,
        platform=version.platform,
        version=version.version,
        build_number=version.build_number,
        release_notes=version.release_notes,
        download_url=version.download_url,
        file_size=version.file_size,
        is_published=version.is_published,
        is_recommended=version.is_recommended,
        published_at=version.published_at,
    )


@router.get("", response_model=AdminVersionListResponse)
def get_versions(
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _: object = Depends(require_current_admin),
    db: Session = Depends(get_db_session),
) -> AdminVersionListResponse:
    items = [_to_response(item).model_dump() for item in list_versions(db, keyword=keyword)]
    sliced, total = paginate_items(items, page=page, page_size=page_size)
    return AdminVersionListResponse(
        items=[AdminVersionResponse(**item) for item in sliced],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=AdminVersionResponse, status_code=status.HTTP_201_CREATED)
def create(payload: AdminVersionCreateRequest, admin=Depends(require_current_admin), db: Session = Depends(get_db_session)) -> AdminVersionResponse:
    version = create_version(
        db,
        platform=payload.platform,
        version=payload.version,
        build_number=payload.build_number,
        release_notes=payload.release_notes,
        download_url=payload.download_url,
        file_size=payload.file_size,
        created_by=admin.username,
    )
    db.commit()
    db.refresh(version)
    return _to_response(version)


@router.post("/{version_id}/publish", response_model=AdminVersionResponse)
def publish(version_id: int, _: object = Depends(require_current_admin), db: Session = Depends(get_db_session)) -> AdminVersionResponse:
    version = get_version(db, version_id=version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="version not found")
    db.commit() if False else None
    publish_version(db, version=version)
    db.commit()
    db.refresh(version)
    return _to_response(version)


@router.post("/{version_id}/unpublish", response_model=AdminVersionResponse)
def unpublish(version_id: int, _: object = Depends(require_current_admin), db: Session = Depends(get_db_session)) -> AdminVersionResponse:
    version = get_version(db, version_id=version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="version not found")
    unpublish_version(db, version=version)
    db.commit()
    db.refresh(version)
    return _to_response(version)


@router.post("/{version_id}/recommend", response_model=AdminVersionResponse)
def recommend(version_id: int, _: object = Depends(require_current_admin), db: Session = Depends(get_db_session)) -> AdminVersionResponse:
    version = get_version(db, version_id=version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="version not found")
    recommend_version(db, version=version)
    db.commit()
    db.refresh(version)
    return _to_response(version)


@router.patch("/{version_id}", response_model=AdminVersionResponse)
def update(version_id: int, payload: AdminVersionUpdateRequest, _: object = Depends(require_current_admin), db: Session = Depends(get_db_session)) -> AdminVersionResponse:
    version = get_version(db, version_id=version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="version not found")
    update_version(db, version=version, release_notes=payload.release_notes, download_url=payload.download_url, file_size=payload.file_size)
    db.commit()
    db.refresh(version)
    return _to_response(version)


@router.delete("/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(version_id: int, _: object = Depends(require_current_admin), db: Session = Depends(get_db_session)):
    version = get_version(db, version_id=version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="version not found")
    try:
        delete_version(db, version=version)
    except PublishedVersionDeleteError as exc:
        raise HTTPException(status_code=409, detail="published version cannot be deleted") from exc
    db.commit()
    return None
