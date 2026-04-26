"""add device location label

Revision ID: 20260426_01
Revises: 20260424_01
Create Date: 2026-04-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260426_01"
down_revision: str | None = "20260424_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("devices", sa.Column("location_label", sa.String(length=128), nullable=False, server_default=""))
    op.alter_column("devices", "location_label", server_default=None)


def downgrade() -> None:
    op.drop_column("devices", "location_label")
