"""add trip datetime and travel fields"""
from alembic import op
import sqlalchemy as sa


revision = "7f2be6d4a8c1"
down_revision = "c4e8f9c2f1ab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "trips",
        "starts_at",
        existing_type=sa.Date(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="starts_at::timestamp with time zone",
    )
    op.alter_column(
        "trips",
        "ends_at",
        existing_type=sa.Date(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="ends_at::timestamp with time zone",
    )
    op.add_column("trips", sa.Column("flight_number", sa.String(), nullable=True))
    op.add_column("trips", sa.Column("airport", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("trips", "airport")
    op.drop_column("trips", "flight_number")
    op.alter_column(
        "trips",
        "ends_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.Date(),
        existing_nullable=True,
        postgresql_using="ends_at::date",
    )
    op.alter_column(
        "trips",
        "starts_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.Date(),
        existing_nullable=True,
        postgresql_using="starts_at::date",
    )
