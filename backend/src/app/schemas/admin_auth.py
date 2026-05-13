from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    username: str = Field(...)
    password: str = Field(...)


class AdminSessionResponse(BaseModel):
    username: str = Field(...)
    display_name: str = Field(...)
    session_token: str = Field(...)


class AdminProfileResponse(BaseModel):
    username: str = Field(...)
    display_name: str = Field(...)
