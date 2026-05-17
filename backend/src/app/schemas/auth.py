from pydantic import BaseModel, Field


class AuthLoginRequest(BaseModel):
    code: str = Field(..., description="微信登录临时凭证 code，由小程序 wx.login() 获取")


class AuthSessionResponse(BaseModel):
    user_id: str = Field(..., description="用户唯一标识（OpenID）")
    session_token: str = Field(..., description="会话令牌，后续请求通过 Header 携带")
    auth_provider: str = Field(..., description="认证方式，固定为 wechat")
    nickname: str | None = Field(None, description="用户昵称")
    avatar_url: str | None = Field(None, description="用户头像 URL")


class UserProfileUpdateRequest(BaseModel):
    nickname: str | None = Field(None, description="用户昵称")
    avatar_url: str | None = Field(None, description="用户头像 URL")


class UserProfileResponse(BaseModel):
    user_id: str = Field(..., description="用户唯一标识")
    nickname: str | None = Field(None, description="用户昵称")
    avatar_url: str | None = Field(None, description="用户头像 URL")


class AvatarUploadTokenResponse(BaseModel):
    upload_url: str = Field(..., description="七牛上传地址")
    token: str = Field(..., description="七牛上传凭证")
    key: str = Field(..., description="头像对象存储路径")
    public_url: str = Field(..., description="头像公开访问 URL")
