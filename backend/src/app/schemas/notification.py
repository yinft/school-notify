from pydantic import BaseModel


class NotificationCreateRequest(BaseModel):
    sender_user_id: str
    title: str
    content: str
    level: str
    device_ids: list[str]


class NotificationCreateResponse(BaseModel):
    status: str
    target_count: int


class NotificationDeliveryRecord(BaseModel):
    device_id: str
    received: bool
    displayed: bool
    spoken: bool


class NotificationRecord(BaseModel):
    notification_id: str
    sender_user_id: str
    title: str
    content: str
    level: str
    target_count: int
    deliveries: list[NotificationDeliveryRecord]


class NotificationRecordListResponse(BaseModel):
    items: list[NotificationRecord]
    total: int = 0
