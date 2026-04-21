from datetime import datetime

from pydantic import BaseModel


class DeviceRegistrationRequest(BaseModel):
    device_id: str
    device_name: str
    client_version: str


class DeviceResponse(BaseModel):
    device_id: str
    device_name: str
    client_version: str
    status: str
    last_seen_at: datetime


class DeviceListResponse(BaseModel):
    items: list[DeviceResponse]
