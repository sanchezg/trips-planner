from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.repositories.session_repository import create_user_session, get_active_session, revoke_session
from tests.factories.user import UserFactory, UserSessionFactory


def test_create_user_session_persists_hashed_token(db_session):
    user = UserFactory()

    session = create_user_session(db_session, user=user, session_token="plain-session-token")

    assert session.user_id == user.id
    assert session.token_hash != "plain-session-token"
    assert session.revoked_at is None


def test_get_active_session_returns_none_for_expired_or_revoked_sessions(db_session):
    user = UserFactory()
    expired = UserSessionFactory(
        user=user,
        token_hash="expired-token-hash",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    revoked = UserSessionFactory(
        user=user,
        token_hash="revoked-token-hash",
        revoked_at=datetime.now(timezone.utc),
    )

    assert get_active_session(db_session, "expired-token") is None
    assert get_active_session(db_session, "revoked-token") is None
    assert expired.id is not None and revoked.id is not None


def test_get_active_session_touches_last_seen_at_for_old_sessions(db_session):
    user = UserFactory()
    session = create_user_session(db_session, user=user, session_token="touch-me")
    previous_seen_at = datetime.now(timezone.utc) - timedelta(hours=1)
    session.last_seen_at = previous_seen_at
    db_session.add(session)
    db_session.commit()

    resolved = get_active_session(db_session, "touch-me")

    assert resolved is not None
    assert resolved.last_seen_at is not None
    assert resolved.last_seen_at > previous_seen_at


def test_revoke_session_marks_session_revoked(db_session):
    user = UserFactory()
    create_user_session(db_session, user=user, session_token="revoke-me")

    revoked = revoke_session(db_session, "revoke-me")
    resolved = get_active_session(db_session, "revoke-me")

    assert revoked is True
    assert resolved is None
