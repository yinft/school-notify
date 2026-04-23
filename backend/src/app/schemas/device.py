from datetime import datetime

from pydantic import BaseModel, Field


class DeviceRegistrationRequest(BaseModel):
    device_id: str = Field(..., description="设备唯一标识，由客户端生成")
    device_name: str = Field(..., description="设备名称，如「教室广播终端 A」")
    client_version: str = Field(..., description="客户端版本号，如 1.0.0")


class DeviceResponse(BaseModel):
    device_id: str = Field(..., description="设备唯一标识")
    device_name: str = Field(..., description="设备名称")
    client_version: str = Field(..., description="客户端版本号")
    status: str = Field(..., description="设备状态：online / offline")
    last_seen_at: datetime = Field(..., description="设备最后心跳时间")
    device_token: str = Field("", description="设备专用令牌，用于 WebSocket 鉴权")


class DeviceListResponse(BaseModel):
    items: list[DeviceResponse] = Field(..., description="设备列表")
