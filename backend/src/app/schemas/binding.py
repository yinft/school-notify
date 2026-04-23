from pydantic import BaseModel, Field


class BindingCodeCreateRequest(BaseModel):
    device_id: str = Field(..., description="设备 ID，由设备端发起绑定码生成")


class BindingCodeResponse(BaseModel):
    device_id: str = Field(..., description="设备 ID")
    code: str = Field(..., description="生成的绑定码（一次性，有时效）")
    expires_in_seconds: int = Field(..., description="绑定码有效时长（秒）")


class BindingCreateRequest(BaseModel):
    user_id: str = Field(..., description="用户 ID")
    code: str = Field(..., description="绑定码，由设备端生成")


class BindingResponse(BaseModel):
    user_id: str = Field(..., description="用户 ID")
    device_id: str = Field(..., description="设备 ID")
