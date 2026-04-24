"""add notification delivery metadata

Revision ID: 20260424_01
Revises: 20260422_02
Create Date: 2026-04-24 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260424_01"
down_revision: str | None = "20260422_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("notifications", sa.Column("duration_seconds", sa.Integer(), nullable=True))
    op.add_column("notifications", sa.Column("tts_enabled", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("notifications", sa.Column("tts_repeat_count", sa.Integer(), nullable=True))
    op.add_column("notification_deliveries", sa.Column("failed", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("notification_deliveries", sa.Column("error_message", sa.String(length=256), nullable=True))
    op.alter_column("notifications", "tts_enabled", server_default=None)
    op.alter_column("notification_deliveries", "failed", server_default=None)


def downgrade() -> None:
    op.drop_column("notification_deliveries", "error_message")
    op.drop_column("notification_deliveries", "failed")
    op.drop_column("notifications", "tts_repeat_count")
    op.drop_column("notifications", "tts_enabled")
    op.drop_column("notifications", "duration_seconds")
