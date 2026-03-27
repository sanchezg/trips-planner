"""add google tokens to users"""
from alembic import op
import sqlalchemy as sa


revision = '6c7e7fb0d991'
down_revision = '1b2ef0a9f3d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('google_access_token', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('google_refresh_token', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('google_token_expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'google_token_expires_at')
    op.drop_column('users', 'google_refresh_token')
    op.drop_column('users', 'google_access_token')
