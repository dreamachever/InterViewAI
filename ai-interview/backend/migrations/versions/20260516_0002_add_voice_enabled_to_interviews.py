"""add voice enabled to interviews

Revision ID: 20260516_0002
Revises: 20260516_0001
Create Date: 2026-05-16
"""
from alembic import op
import sqlalchemy as sa


revision = "20260516_0002"
down_revision = "20260516_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("interviews", sa.Column("voice_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.alter_column("interviews", "voice_enabled", server_default=None)


def downgrade() -> None:
    op.drop_column("interviews", "voice_enabled")
