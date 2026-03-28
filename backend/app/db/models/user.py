import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.crypto import decrypt_secret, encrypt_secret
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    google_sub: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    _google_access_token_encrypted: Mapped[str | None] = mapped_column("google_access_token", Text, nullable=True)
    _google_refresh_token_encrypted: Mapped[str | None] = mapped_column("google_refresh_token", Text, nullable=True)
    google_token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    trips = relationship("Trip", back_populates="owner")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    @property
    def google_access_token(self) -> str | None:
        return decrypt_secret(self._google_access_token_encrypted)

    @google_access_token.setter
    def google_access_token(self, value: str | None) -> None:
        self._google_access_token_encrypted = encrypt_secret(value)

    @property
    def google_refresh_token(self) -> str | None:
        return decrypt_secret(self._google_refresh_token_encrypted)

    @google_refresh_token.setter
    def google_refresh_token(self, value: str | None) -> None:
        self._google_refresh_token_encrypted = encrypt_secret(value)
