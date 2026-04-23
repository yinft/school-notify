from pydantic import BaseModel, Field


class AuthLoginRequest(BaseModel):
    code: str = Field(..., description="微信登录临时凭证 code，由小程序 wx.login() 获取")


class AuthSessionResponse(BaseModel):
    user_id: str = Field(..., description="用户唯一标识（OpenID）")
    session_token: str = Field(..., description="会话令牌，后续请求通过 Header 携带")
    auth_provider: str = Field(..., description="认证方式，固定为 wechat")


class UserProfileUpdateRequest(BaseModel):
    nickname: str | None = Field(None, description="用户昵称")
    avatar_url: str | None = Field(None, description="用户头像 URL")


class UserProfileResponse(BaseModel):
    user_id: str = Field(..., description="用户唯一标识")
    nickname: str | None = Field(None, description="用户昵称")
    avatar_url: str | None = Field(None, description="用户头像 URL")
