"""add role based trip sharing"""
from alembic import op
import sqlalchemy as sa


revision = "c4e8f9c2f1ab"
down_revision = "9d3c40d5a7ef"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trip_share_codes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("trip_id", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_trip_share_codes_code"),
        sa.UniqueConstraint("trip_id", "role", name="uq_trip_share_codes_trip_role"),
    )


def downgrade() -> None:
    op.drop_table("trip_share_codes")
