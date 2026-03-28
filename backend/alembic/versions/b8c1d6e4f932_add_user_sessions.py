"""add user sessions"""
from alembic import op
import sqlalchemy as sa


revision = "b8c1d6e4f932"
down_revision = "7f2be6d4a8c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_sessions_token_hash", "user_sessions", ["token_hash"], unique=True)
    op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_user_sessions_user_id", table_name="user_sessions")
    op.drop_index("ix_user_sessions_token_hash", table_name="user_sessions")
    op.drop_table("user_sessions")
