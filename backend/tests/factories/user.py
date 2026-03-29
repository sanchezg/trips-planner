from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import factory

from app.core.security import hash_session_token
from app.db.models.user import User
from app.db.models.user_session import UserSession
from tests.factories.base import SQLAlchemySessionFactory


class UserFactory(SQLAlchemySessionFactory):
    class Meta:
        model = User

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = factory.Sequence(lambda n: f"User {n}")
    avatar_url = None
    google_sub = factory.Sequence(lambda n: f"google-sub-{n}")


class UserSessionFactory(SQLAlchemySessionFactory):
    class Meta:
        model = UserSession

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    user = factory.SubFactory(UserFactory)
    user_id = factory.SelfAttribute("user.id")
    token_hash = factory.Sequence(lambda n: hash_session_token(f"session-token-{n}"))
    expires_at = factory.LazyFunction(lambda: datetime.now(timezone.utc) + timedelta(days=7))
    last_seen_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    revoked_at = None
