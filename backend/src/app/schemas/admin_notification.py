from pydantic import BaseModel


class AdminNotificationDeliveryItem(BaseModel):
    device_id: str
    device_name: str
    received: bool
    displayed: bool
    spoken: bool
    failed: bool
    error_message: str | None


class AdminNotificationListItem(BaseModel):
    notification_id: str
    sender_user_id: str
    title: str
    created_at: str
    success_count: int
    failed_count: int


class AdminNotificationListResponse(BaseModel):
    items: list[AdminNotificationListItem]
    total: int
    page: int
    page_size: int


class AdminNotificationDetailResponse(BaseModel):
    notification_id: str
    sender_user_id: str
    title: str
    content: str
    created_at: str
    deliveries: list[AdminNotificationDeliveryItem]
