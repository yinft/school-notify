from pydantic import BaseModel


class AdminUserDeviceSummary(BaseModel):
    device_id: str
    device_name: str
    location_label: str
    client_version: str
    status: str


class AdminUserNotificationSummary(BaseModel):
    notification_id: str
    title: str
    created_at: str


class AdminUserListItem(BaseModel):
    user_id: str
    nickname: str | None
    avatar_url: str | None
    bound_devices_count: int


class AdminUserListResponse(BaseModel):
    items: list[AdminUserListItem]
    total: int
    page: int
    page_size: int


class AdminUserDetailResponse(BaseModel):
    user_id: str
    nickname: str | None
    avatar_url: str | None
    devices: list[AdminUserDeviceSummary]
    recent_notifications: list[AdminUserNotificationSummary]
