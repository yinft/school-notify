"""initial schema

Revision ID: 20260422_01
Revises: 
Create Date: 2026-04-22 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260422_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("openid", sa.String(length=128), nullable=False),
        sa.Column("nickname", sa.String(length=128), nullable=True),
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_user_id", "users", ["user_id"], unique=True)
    op.create_index("ix_users_openid", "users", ["openid"], unique=True)

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("session_token", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"], unique=False)
    op.create_index("ix_auth_sessions_session_token", "auth_sessions", ["session_token"], unique=True)

    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("device_id", sa.String(length=128), nullable=False),
        sa.Column("device_name", sa.String(length=128), nullable=False),
        sa.Column("client_version", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_devices_device_id", "devices", ["device_id"], unique=True)

    op.create_table(
        "device_bind_codes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("device_id", sa.String(length=128), nullable=False),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("expires_in_seconds", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_device_bind_codes_device_id", "device_bind_codes", ["device_id"], unique=False)
    op.create_index("ix_device_bind_codes_code", "device_bind_codes", ["code"], unique=True)

    op.create_table(
        "user_devices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("device_id", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_user_devices_user_id", "user_devices", ["user_id"], unique=False)
    op.create_index("ix_user_devices_device_id", "user_devices", ["device_id"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("notification_id", sa.String(length=128), nullable=False),
        sa.Column("sender_user_id", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("content", sa.String(length=2048), nullable=False),
        sa.Column("level", sa.String(length=32), nullable=False),
        sa.Column("target_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_notifications_notification_id", "notifications", ["notification_id"], unique=True)
    op.create_index("ix_notifications_sender_user_id", "notifications", ["sender_user_id"], unique=False)

    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("notification_id", sa.String(length=128), nullable=False),
        sa.Column("device_id", sa.String(length=128), nullable=False),
        sa.Column("received", sa.Boolean(), nullable=False),
        sa.Column("displayed", sa.Boolean(), nullable=False),
        sa.Column("spoken", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_notification_deliveries_notification_id", "notification_deliveries", ["notification_id"], unique=False)
    op.create_index("ix_notification_deliveries_device_id", "notification_deliveries", ["device_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_notification_deliveries_device_id", table_name="notification_deliveries")
    op.drop_index("ix_notification_deliveries_notification_id", table_name="notification_deliveries")
    op.drop_table("notification_deliveries")

    op.drop_index("ix_notifications_sender_user_id", table_name="notifications")
    op.drop_index("ix_notifications_notification_id", table_name="notifications")
    op.drop_table("notifications")

    op.drop_index("ix_user_devices_device_id", table_name="user_devices")
    op.drop_index("ix_user_devices_user_id", table_name="user_devices")
    op.drop_table("user_devices")

    op.drop_index("ix_device_bind_codes_code", table_name="device_bind_codes")
    op.drop_index("ix_device_bind_codes_device_id", table_name="device_bind_codes")
    op.drop_table("device_bind_codes")

    op.drop_index("ix_devices_device_id", table_name="devices")
    op.drop_table("devices")

    op.drop_index("ix_auth_sessions_session_token", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")

    op.drop_index("ix_users_openid", table_name="users")
    op.drop_index("ix_users_user_id", table_name="users")
    op.drop_table("users")
