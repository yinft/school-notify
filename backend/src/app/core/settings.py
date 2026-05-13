from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "school-notify-backend"
    debug: bool = False
    sql_echo: bool = False
    database_url: str = "postgresql+psycopg://postgres:123@localhost:5432/school"
    bind_code_expires_seconds: int = 60
    wechat_app_id: str = ""
    wechat_app_secret: str = ""
    wechat_code2session_url: str = "https://api.weixin.qq.com/sns/jscode2session"
    session_signing_secret: str = "school-notify-dev-secret"
    admin_username: str = "admin"
    admin_password: str = "pass123456"
    admin_display_name: str = "系统管理员"
    redis_url: str = ""
    redis_password: str = ""
    redis_key_prefix: str = "school-notify"
    auth_session_cache_ttl_seconds: int = 7200
    device_online_ttl_seconds: int = 60

    model_config = SettingsConfigDict(
        env_prefix="SCHOOL_NOTIFY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
