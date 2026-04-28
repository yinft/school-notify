from pydantic import BaseModel, Field


class NotificationCreateRequest(BaseModel):
    sender_user_id: str = Field(..., description="发送者用户 ID")
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    level: str = Field(..., description="通知级别，如 info / warning / urgent")
    device_ids: list[str] = Field(..., min_length=1, description="目标设备 ID 列表")
    duration_seconds: int | None = Field(None, ge=1, description="通知展示时长，单位秒")
    tts_enabled: bool = Field(True, description="是否启用语音播报")
    tts_repeat_count: int | None = Field(None, ge=1, description="语音播报重复次数")


class NotificationCreateResponse(BaseModel):
    status: str = Field(..., description="处理结果状态，如 accepted")
    target_count: int = Field(..., description="目标设备数量")


class NotificationDeliveryRecord(BaseModel):
    device_id: str = Field(..., description="设备 ID")
    device_name: str = Field("", description="设备名称")
    location_label: str = Field("", description="设备位置描述")
    received: bool = Field(..., description="设备是否已收到通知")
    displayed: bool = Field(..., description="设备是否已展示通知")
    spoken: bool = Field(..., description="设备是否已语音播报通知")
    failed: bool = Field(False, description="设备投递是否失败")
    error_message: str | None = Field(None, description="投递失败原因")


class NotificationRecord(BaseModel):
    notification_id: str = Field(..., description="通知唯一 ID")
    sender_user_id: str = Field(..., description="发送者用户 ID")
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    level: str = Field(..., description="通知级别")
    duration_seconds: int | None = Field(None, description="通知展示时长，单位秒")
    tts_enabled: bool = Field(True, description="是否启用语音播报")
    tts_repeat_count: int | None = Field(None, description="语音播报重复次数")
    target_count: int = Field(..., description="目标设备数量")
    created_at: str = Field(..., description="通知创建时间")
    deliveries: list[NotificationDeliveryRecord] = Field(..., description="各设备的投递状态")


class NotificationRecordListResponse(BaseModel):
    items: list[NotificationRecord] = Field(..., description="通知记录列表")
    total: int = Field(0, description="符合条件的总记录数")
