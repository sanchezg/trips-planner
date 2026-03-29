from __future__ import annotations

from datetime import timedelta

from tests.factories.event import EventFactory
from tests.factories.trip import TripFactory, TripMemberFactory
from tests.factories.user import UserFactory


def test_create_event_requires_editor_role(client, db_session):
    trip = TripFactory()
    viewer = UserFactory(email="viewer@example.com")
    TripMemberFactory(trip=trip, user=viewer, role="viewer")

    from app.repositories.session_repository import create_user_session

    session_token = "session-token-viewer"
    create_user_session(db_session, user=viewer, session_token=session_token)
    client.cookies.set("trip_session", session_token)

    response = client.post(
        "/api/routes/events",
        json={
            "trip_id": trip.id,
            "title": "Forbidden event",
            "starts_at": trip.starts_at.isoformat(),
            "ends_at": (trip.starts_at + timedelta(hours=1)).isoformat(),
        },
    )

    assert response.status_code == 404


def test_create_event_returns_conflict_warnings(authenticated_client, mocker):
    client, user = authenticated_client
    trip = TripFactory(owner=user)
    EventFactory(trip=trip, starts_at=trip.starts_at, ends_at=trip.starts_at + timedelta(hours=2), title="Existing")
    mocker.patch("app.api.routes.events.detect_conflicts", return_value=["Overlap warning"])

    response = client.post(
        "/api/routes/events",
        json={
            "trip_id": trip.id,
            "title": "Museum visit",
            "starts_at": (trip.starts_at + timedelta(minutes=30)).isoformat(),
            "ends_at": (trip.starts_at + timedelta(hours=1, minutes=30)).isoformat(),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["event"]["title"] == "Museum visit"
    assert payload["warnings"] == ["Overlap warning"]
