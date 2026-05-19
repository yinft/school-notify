from datetime import datetime

from pydantic import BaseModel, Field, field_validator


VERSION_PATTERN_ERROR = "version must use numeric dot notation like 1.0.0"


def _normalize_version(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(VERSION_PATTERN_ERROR)

    parts = normalized.split(".")
    if len(parts) < 2 or any(not part.isdigit() for part in parts):
        raise ValueError(VERSION_PATTERN_ERROR)

    return normalized


class AdminVersionCreateRequest(BaseModel):
    platform: str = Field(...)
    version: str = Field(...)
    build_number: str = Field("")
    release_notes: str = Field("")
    download_url: str = Field(...)
    file_size: int | None = Field(None)

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: str) -> str:
        return _normalize_version(value)


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
    is_recommended: bool


class PublicVersionListResponse(BaseModel):
    items: list[PublicVersionResponse]
