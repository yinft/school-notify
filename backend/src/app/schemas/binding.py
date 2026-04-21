from pydantic import BaseModel


class BindingCodeCreateRequest(BaseModel):
    device_id: str


class BindingCodeResponse(BaseModel):
    device_id: str
    code: str
    expires_in_seconds: int


class BindingCreateRequest(BaseModel):
    user_id: str
    code: str


class BindingResponse(BaseModel):
    user_id: str
    device_id: str
