from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ClientVersion


class PublishedVersionDeleteError(Exception):
    pass


def create_version(db: Session, **kwargs: object) -> ClientVersion:
    version = ClientVersion(**kwargs)
    db.add(version)
    db.flush()
    return version


def list_versions(db: Session, *, keyword: str | None = None) -> list[ClientVersion]:
    items = db.execute(select(ClientVersion).order_by(ClientVersion.id.desc())).scalars().all()
    if not keyword:
        return items
    return [
        item
        for item in items
        if keyword in item.version or keyword in item.release_notes or keyword in item.build_number
    ]


def get_version(db: Session, *, version_id: int) -> ClientVersion | None:
    return db.execute(select(ClientVersion).where(ClientVersion.id == version_id)).scalar_one_or_none()


def update_version(db: Session, *, version: ClientVersion, release_notes: str | None, download_url: str | None, file_size: int | None) -> ClientVersion:
    if release_notes is not None:
        version.release_notes = release_notes
    if download_url is not None:
        version.download_url = download_url
    if file_size is not None:
        version.file_size = file_size
    version.updated_at = datetime.now()
    db.flush()
    return version


def publish_version(db: Session, *, version: ClientVersion) -> ClientVersion:
    version.is_published = True
    version.published_at = datetime.now()
    db.flush()
    return version


def unpublish_version(db: Session, *, version: ClientVersion) -> ClientVersion:
    version.is_published = False
    version.is_recommended = False
    db.flush()
    return version


def recommend_version(db: Session, *, version: ClientVersion) -> ClientVersion:
    versions = db.execute(select(ClientVersion).where(ClientVersion.platform == version.platform)).scalars().all()
    for item in versions:
        item.is_recommended = item.id == version.id and item.is_published
    db.flush()
    return version


def delete_version(db: Session, *, version: ClientVersion) -> None:
    if version.is_published:
        raise PublishedVersionDeleteError
    db.delete(version)
    db.flush()


def list_public_versions(db: Session, *, platform: str | None) -> list[ClientVersion]:
    stmt = select(ClientVersion).where(ClientVersion.is_published.is_(True)).order_by(ClientVersion.published_at.desc(), ClientVersion.id.desc())
    if platform:
        stmt = stmt.where(ClientVersion.platform == platform)
    return db.execute(stmt).scalars().all()
