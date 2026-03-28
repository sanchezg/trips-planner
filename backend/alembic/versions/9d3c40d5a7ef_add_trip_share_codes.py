"""add trip share codes"""
from alembic import op
import sqlalchemy as sa


revision = '9d3c40d5a7ef'
down_revision = '6c7e7fb0d991'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('trips', sa.Column('share_code', sa.String(), nullable=True))
    op.create_unique_constraint('uq_trips_share_code', 'trips', ['share_code'])


def downgrade() -> None:
    op.drop_constraint('uq_trips_share_code', 'trips', type_='unique')
    op.drop_column('trips', 'share_code')
