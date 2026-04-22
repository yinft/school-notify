"""add unique constraints

Revision ID: 20260422_02
Revises: 20260422_01
Create Date: 2026-04-22 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op


revision: str = "20260422_02"
down_revision: str | None = "20260422_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint("uq_user_devices_user_device", "user_devices", ["user_id", "device_id"])
    op.create_unique_constraint("uq_notification_deliveries_notification_device", "notification_deliveries", ["notification_id", "device_id"])


def downgrade() -> None:
    op.drop_constraint("uq_notification_deliveries_notification_device", "notification_deliveries", type_="unique")
    op.drop_constraint("uq_user_devices_user_device", "user_devices", type_="unique")
