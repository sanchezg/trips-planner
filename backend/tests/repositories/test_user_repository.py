from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.repositories.user_repository import get_by_google_sub, get_or_create_google_user


def test_get_or_create_google_user_creates_new_user(db_session):
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    user = get_or_create_google_user(
        db_session,
        email="new@example.com",
        name="New User",
        avatar_url="https://example.com/avatar.png",
        google_sub="google-sub-new",
        google_access_token="access-token",
        google_refresh_token="refresh-token",
        google_token_expires_at=expires_at,
    )

    assert user.email == "new@example.com"
    assert user.google_sub == "google-sub-new"
    assert user.google_access_token == "access-token"
    assert user.google_refresh_token == "refresh-token"
    assert get_by_google_sub(db_session, "google-sub-new").id == user.id


def test_get_or_create_google_user_updates_existing_user_without_overwriting_refresh_token_with_none(db_session):
    original = get_or_create_google_user(
        db_session,
        email="first@example.com",
        name="First Name",
        avatar_url=None,
        google_sub="google-sub-existing",
        google_access_token="first-access",
        google_refresh_token="first-refresh",
        google_token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    updated = get_or_create_google_user(
        db_session,
        email="updated@example.com",
        name="Updated Name",
        avatar_url="https://example.com/new-avatar.png",
        google_sub="google-sub-existing",
        google_access_token="second-access",
        google_refresh_token=None,
        google_token_expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
    )

    assert updated.id == original.id
    assert updated.email == "updated@example.com"
    assert updated.name == "Updated Name"
    assert updated.avatar_url == "https://example.com/new-avatar.png"
    assert updated.google_access_token == "second-access"
    assert updated.google_refresh_token == "first-refresh"
