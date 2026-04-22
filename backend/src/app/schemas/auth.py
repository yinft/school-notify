from pydantic import BaseModel


class AuthLoginRequest(BaseModel):
    code: str


class AuthSessionResponse(BaseModel):
    user_id: str
    session_token: str
    auth_provider: str


class UserProfileUpdateRequest(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None


class UserProfileResponse(BaseModel):
    user_id: str
    nickname: str | None
    avatar_url: str | None
