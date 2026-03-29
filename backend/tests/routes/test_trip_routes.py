from __future__ import annotations

from app.repositories.trip_repository import TRIP_ROLE_EDITOR
from tests.factories.trip import TripFactory, TripMemberFactory, TripShareCodeFactory
from tests.factories.user import UserFactory


def test_join_trip_by_share_code_grants_membership(client, db_session):
    owner = UserFactory()
    trip = TripFactory(owner=owner)
    share_code = TripShareCodeFactory(trip=trip, role=TRIP_ROLE_EDITOR, code="JOINME12")
    joining_user = UserFactory(email="joiner@example.com")

    from app.repositories.session_repository import create_user_session

    session_token = "session-token-joiner"
    create_user_session(db_session, user=joining_user, session_token=session_token)
    client.cookies.set("trip_session", session_token)

    response = client.post("/api/routes/trips/join", json={"code": share_code.code})

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == trip.id
    assert payload["membership_role"] == TRIP_ROLE_EDITOR


def test_get_trips_includes_owned_and_shared_trips(authenticated_client):
    client, user = authenticated_client
    owned_trip = TripFactory(owner=user)
    shared_trip = TripFactory()
    TripMemberFactory(trip=shared_trip, user=user, role="viewer")

    response = client.get("/api/routes/trips")

    assert response.status_code == 200
    trip_ids = {trip["id"] for trip in response.json()}
    assert owned_trip.id in trip_ids
    assert shared_trip.id in trip_ids
