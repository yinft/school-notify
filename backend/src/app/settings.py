from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "school-notify-backend"
    debug: bool = False
    bind_code_expires_seconds: int = 300

    model_config = SettingsConfigDict(env_prefix="SCHOOL_NOTIFY_", extra="ignore")


settings = Settings()
