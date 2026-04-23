from pydantic import BaseModel, Field


class NotificationCreateRequest(BaseModel):
    sender_user_id: str = Field(..., description="发送者用户 ID")
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    level: str = Field(..., description="通知级别，如 info / warning / urgent")
    device_ids: list[str] = Field(..., description="目标设备 ID 列表")


class NotificationCreateResponse(BaseModel):
    status: str = Field(..., description="处理结果状态，如 accepted")
    target_count: int = Field(..., description="目标设备数量")


class NotificationDeliveryRecord(BaseModel):
    device_id: str = Field(..., description="设备 ID")
    received: bool = Field(..., description="设备是否已收到通知")
    displayed: bool = Field(..., description="设备是否已展示通知")
    spoken: bool = Field(..., description="设备是否已语音播报通知")


class NotificationRecord(BaseModel):
    notification_id: str = Field(..., description="通知唯一 ID")
    sender_user_id: str = Field(..., description="发送者用户 ID")
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    level: str = Field(..., description="通知级别")
    target_count: int = Field(..., description="目标设备数量")
    deliveries: list[NotificationDeliveryRecord] = Field(..., description="各设备的投递状态")


class NotificationRecordListResponse(BaseModel):
    items: list[NotificationRecord] = Field(..., description="通知记录列表")
    total: int = Field(0, description="符合条件的总记录数")
