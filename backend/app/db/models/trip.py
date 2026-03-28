import uuid
from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

DEFAULT_EVENT_CATEGORIES = ["transit", "travel", "stay", "entertainment", "meal"]


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    starts_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    ends_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    visibility: Mapped[str] = mapped_column(String, default="private")
    share_code: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    event_categories: Mapped[list[str]] = mapped_column(JSON, default=lambda: DEFAULT_EVENT_CATEGORIES.copy())
    calendar_auto_sync: Mapped[bool] = mapped_column(Boolean, default=False)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="trips")
