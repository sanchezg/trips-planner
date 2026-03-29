from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

from app.core.security import hash_session_token
from app.db.models.user import User
from app.db.models.user_session import UserSession
from app.dependencies.auth import get_current_user


def test_google_login_sets_oauth_state_cookie_and_preserves_next_path(client):
    response = client.get("/api/routes/auth/google/login", params={"next": "/join/SHARE123"}, follow_redirects=False)

    assert response.status_code in {302, 307}
    assert "state=" in response.headers["location"]
    assert "trip_oauth_state" in response.cookies


def test_google_callback_creates_server_side_session_and_redirects_to_next_path(client, db_session, mocker):
    login_response = client.get("/api/routes/auth/google/login", params={"next": "/join/SHARE123"}, follow_redirects=False)
    state = parse_qs(urlparse(login_response.headers["location"]).query)["state"][0]

    mocker.patch(
        "app.api.routes.auth.exchange_code_for_user",
        return_value={
            "email": "allowed@example.com",
            "name": "Allowed User",
            "picture": "https://example.com/avatar.png",
            "sub": "google-sub-allowed",
            "access_token": "access-token",
            "refresh_token": "refresh-token",
            "token_expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
        },
    )

    response = client.get(
        "/api/routes/auth/google/callback",
        params={"code": "oauth-code", "state": state},
        cookies={"trip_oauth_state": login_response.cookies["trip_oauth_state"]},
        follow_redirects=False,
    )

    assert response.status_code in {302, 307}
    assert response.headers["location"] == "http://testserver/join/SHARE123"

    session_cookie = response.cookies.get("trip_session")
    assert session_cookie is not None
    assert db_session.query(User).filter(User.email == "allowed@example.com").count() == 1
    assert db_session.query(UserSession).filter(UserSession.token_hash == hash_session_token(session_cookie)).count() == 1


def test_google_callback_rejects_disallowed_email(client, db_session, mocker):
    login_response = client.get("/api/routes/auth/google/login", follow_redirects=False)
    state = parse_qs(urlparse(login_response.headers["location"]).query)["state"][0]
    mocker.patch.object(get_current_user.__globals__["settings"], "auth_allowed_emails", "allowed@example.com")
    mocker.patch.object(get_current_user.__globals__["settings"], "auth_allowed_domains", "")
    mocker.patch(
        "app.api.routes.auth.exchange_code_for_user",
        return_value={
            "email": "blocked@example.com",
            "name": "Blocked User",
            "picture": None,
            "sub": "google-sub-blocked",
            "access_token": "access-token",
            "refresh_token": None,
            "token_expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
        },
    )

    response = client.get(
        "/api/routes/auth/google/callback",
        params={"code": "oauth-code", "state": state},
        cookies={"trip_oauth_state": login_response.cookies["trip_oauth_state"]},
        follow_redirects=False,
    )

    assert response.status_code in {302, 307}
    assert response.headers["location"] == "http://testserver/login?error=unauthorized_email"
    assert db_session.query(User).count() == 0
    assert db_session.query(UserSession).count() == 0
