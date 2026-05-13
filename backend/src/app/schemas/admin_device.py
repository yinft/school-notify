from pydantic import BaseModel


class AdminDeviceUserSummary(BaseModel):
    user_id: str
    nickname: str | None


class AdminDeviceNotificationSummary(BaseModel):
    notification_id: str
    title: str
    sender_user_id: str


class AdminDeviceListItem(BaseModel):
    device_id: str
    device_name: str
    location_label: str
    client_version: str
    status: str
    bound_users_count: int


class AdminDeviceListResponse(BaseModel):
    items: list[AdminDeviceListItem]
    total: int
    page: int
    page_size: int


class AdminDeviceDetailResponse(BaseModel):
    device_id: str
    device_name: str
    location_label: str
    client_version: str
    status: str
    bound_users: list[AdminDeviceUserSummary]
    recent_notifications: list[AdminDeviceNotificationSummary]


class AdminDeviceUpdateRequest(BaseModel):
    device_name: str | None = None
    location_label: str | None = None
