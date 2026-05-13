from datetime import datetime

from pydantic import BaseModel, Field


class AdminVersionCreateRequest(BaseModel):
    platform: str = Field(...)
    version: str = Field(...)
    build_number: str = Field("")
    release_notes: str = Field("")
    download_url: str = Field(...)
    file_size: int | None = Field(None)


class AdminVersionUpdateRequest(BaseModel):
    release_notes: str | None = Field(None)
    download_url: str | None = Field(None)
    file_size: int | None = Field(None)


class AdminVersionResponse(BaseModel):
    id: int
    platform: str
    version: str
    build_number: str
    release_notes: str
    download_url: str
    file_size: int | None
    is_published: bool
    is_recommended: bool
    published_at: datetime | None


class AdminVersionListResponse(BaseModel):
    items: list[AdminVersionResponse]
    total: int
    page: int
    page_size: int


class PublicVersionResponse(BaseModel):
    platform: str
    version: str
    release_notes: str
    download_url: str
    file_size: int | None
    published_at: datetime | None


class PublicVersionListResponse(BaseModel):
    items: list[PublicVersionResponse]
