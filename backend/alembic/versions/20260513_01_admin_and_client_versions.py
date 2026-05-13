"""add admin auth and client versions

Revision ID: 20260513_01
Revises: 20260426_01
Create Date: 2026-05-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260513_01"
down_revision: str | None = "20260426_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_admin_users_username", "admin_users", ["username"], unique=True)

    op.create_table(
        "admin_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("admin_user_id", sa.Integer(), nullable=False),
        sa.Column("session_token", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["admin_user_id"], ["admin_users.id"]),
    )
    op.create_index("ix_admin_sessions_admin_user_id", "admin_sessions", ["admin_user_id"], unique=False)
    op.create_index("ix_admin_sessions_session_token", "admin_sessions", ["session_token"], unique=True)

    op.create_table(
        "client_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("platform", sa.String(length=32), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("build_number", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("release_notes", sa.String(length=2048), nullable=False, server_default=""),
        sa.Column("download_url", sa.String(length=1024), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_recommended", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_client_versions_platform", "client_versions", ["platform"], unique=False)
    op.create_index("ix_client_versions_version", "client_versions", ["version"], unique=False)

    op.alter_column("admin_users", "is_active", server_default=None)
    op.alter_column("client_versions", "build_number", server_default=None)
    op.alter_column("client_versions", "release_notes", server_default=None)
    op.alter_column("client_versions", "created_by", server_default=None)
    op.alter_column("client_versions", "is_published", server_default=None)
    op.alter_column("client_versions", "is_recommended", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_client_versions_version", table_name="client_versions")
    op.drop_index("ix_client_versions_platform", table_name="client_versions")
    op.drop_table("client_versions")
    op.drop_index("ix_admin_sessions_session_token", table_name="admin_sessions")
    op.drop_index("ix_admin_sessions_admin_user_id", table_name="admin_sessions")
    op.drop_table("admin_sessions")
    op.drop_index("ix_admin_users_username", table_name="admin_users")
    op.drop_table("admin_users")
