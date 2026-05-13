from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    openid: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    nickname: Mapped[str | None] = mapped_column(String(128), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
    )

    auth_sessions: Mapped[list["AuthSession"]] = relationship(back_populates="user")


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    session_token: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="auth_sessions")


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    display_name: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
    )


class AdminSession(Base):
    __tablename__ = "admin_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_user_id: Mapped[int] = mapped_column(ForeignKey("admin_users.id"), index=True)
    session_token: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ClientVersion(Base):
    __tablename__ = "client_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    platform: Mapped[str] = mapped_column(String(32), index=True)
    version: Mapped[str] = mapped_column(String(64), index=True)
    build_number: Mapped[str] = mapped_column(String(64), default="")
    release_notes: Mapped[str] = mapped_column(String(2048), default="")
    download_url: Mapped[str] = mapped_column(String(1024))
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
    )


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    device_name: Mapped[str] = mapped_column(String(128))
    location_label: Mapped[str] = mapped_column(String(128), default="")
    client_version: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="online")
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now())


class DeviceBindCode(Base):
    __tablename__ = "device_bind_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(128), index=True)
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    expires_in_seconds: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now())


class UserDevice(Base):
    __tablename__ = "user_devices"
    __table_args__ = (
        UniqueConstraint("user_id", "device_id", name="uq_user_devices_user_device"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    device_id: Mapped[str] = mapped_column(String(128), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now())


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    notification_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    sender_user_id: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(256))
    content: Mapped[str] = mapped_column(String(2048))
    level: Mapped[str] = mapped_column(String(32))
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tts_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    tts_repeat_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_count: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now())


class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"
    __table_args__ = (
        UniqueConstraint("notification_id", "device_id", name="uq_notification_deliveries_notification_device"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    notification_id: Mapped[str] = mapped_column(String(128), index=True)
    device_id: Mapped[str] = mapped_column(String(128), index=True)
    received: Mapped[bool] = mapped_column(Boolean, default=False)
    displayed: Mapped[bool] = mapped_column(Boolean, default=False)
    spoken: Mapped[bool] = mapped_column(Boolean, default=False)
    failed: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[str | None] = mapped_column(String(256), nullable=True)
