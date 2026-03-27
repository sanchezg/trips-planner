"""add trip settings"""
from alembic import op
import sqlalchemy as sa


revision = '1b2ef0a9f3d4'
down_revision = 'f0e2b0461893'
branch_labels = None
depends_on = None


DEFAULT_EVENT_CATEGORIES = '["transit", "travel", "stay", "entertainment", "meal"]'


def upgrade() -> None:
    op.add_column('trips', sa.Column('event_categories', sa.JSON(), nullable=True))
    op.add_column('trips', sa.Column('calendar_auto_sync', sa.Boolean(), nullable=True))
    op.execute(f"UPDATE trips SET event_categories = '{DEFAULT_EVENT_CATEGORIES}'::json, calendar_auto_sync = false WHERE event_categories IS NULL OR calendar_auto_sync IS NULL")
    op.alter_column('trips', 'event_categories', nullable=False)
    op.alter_column('trips', 'calendar_auto_sync', nullable=False)


def downgrade() -> None:
    op.drop_column('trips', 'calendar_auto_sync')
    op.drop_column('trips', 'event_categories')
