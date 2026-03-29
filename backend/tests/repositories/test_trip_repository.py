from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.repositories.trip_repository import (
    TRIP_ROLE_EDITOR,
    TRIP_ROLE_OWNER,
    TRIP_ROLE_VIEWER,
    create_share_code,
    get_for_user,
    get_trip_for_min_role,
    get_trip_role,
    has_required_role,
    join_trip_by_code,
    list_for_user,
    update_trip_settings,
)
from tests.factories.trip import TripFactory, TripMemberFactory, TripShareCodeFactory
from tests.factories.user import UserFactory


def test_list_for_user_includes_owned_and_active_shared_trips_only(db_session):
    user = UserFactory()
    owned_trip = TripFactory(owner=user, starts_at=datetime.now(timezone.utc) + timedelta(days=2))
    active_shared_trip = TripFactory(ends_at=datetime.now(timezone.utc) + timedelta(days=1))
    TripMemberFactory(trip=active_shared_trip, user=user, role=TRIP_ROLE_VIEWER)
    expired_shared_trip = TripFactory(ends_at=datetime.now(timezone.utc) - timedelta(days=1))
    TripMemberFactory(trip=expired_shared_trip, user=user, role=TRIP_ROLE_VIEWER)

    trips = list_for_user(db_session, user.id)

    trip_ids = {trip.id for trip in trips}
    assert owned_trip.id in trip_ids
    assert active_shared_trip.id in trip_ids
    assert expired_shared_trip.id not in trip_ids


def test_get_for_user_returns_owned_trip_even_if_past(db_session):
    owner = UserFactory()
    trip = TripFactory(owner=owner, ends_at=datetime.now(timezone.utc) - timedelta(days=3))

    resolved = get_for_user(db_session, trip.id, owner.id)

    assert resolved is not None
    assert resolved.id == trip.id


def test_get_trip_role_returns_none_for_expired_shared_trip(db_session):
    user = UserFactory()
    trip = TripFactory(ends_at=datetime.now(timezone.utc) - timedelta(hours=1))
    TripMemberFactory(trip=trip, user=user, role=TRIP_ROLE_EDITOR)

    assert get_trip_role(db_session, trip, user.id) is None


def test_get_trip_for_min_role_respects_role_order(db_session):
    user = UserFactory()
    trip = TripFactory()
    TripMemberFactory(trip=trip, user=user, role=TRIP_ROLE_VIEWER)

    assert get_trip_for_min_role(db_session, trip.id, user.id, TRIP_ROLE_VIEWER) is not None
    assert get_trip_for_min_role(db_session, trip.id, user.id, TRIP_ROLE_EDITOR) is None
    assert has_required_role(TRIP_ROLE_OWNER, TRIP_ROLE_EDITOR) is True
    assert has_required_role(TRIP_ROLE_VIEWER, TRIP_ROLE_EDITOR) is False


def test_create_share_code_reuses_existing_code_for_role(db_session):
    trip = TripFactory()

    first = create_share_code(db_session, trip, TRIP_ROLE_VIEWER)
    second = create_share_code(db_session, trip, TRIP_ROLE_VIEWER)

    assert first.id == second.id
    assert first.code == second.code


def test_join_trip_by_code_creates_and_upgrades_membership(db_session):
    trip = TripFactory()
    user = UserFactory()
    viewer_code = TripShareCodeFactory(trip=trip, role=TRIP_ROLE_VIEWER, code="VIEWCODE")
    editor_code = TripShareCodeFactory(trip=trip, role=TRIP_ROLE_EDITOR, code="EDITCODE")

    joined_trip = join_trip_by_code(db_session, code=viewer_code.code.lower(), user_id=user.id)
    assert joined_trip is not None
    assert get_trip_role(db_session, trip, user.id) == TRIP_ROLE_VIEWER

    upgraded_trip = join_trip_by_code(db_session, code=editor_code.code, user_id=user.id)
    assert upgraded_trip is not None
    assert get_trip_role(db_session, trip, user.id) == TRIP_ROLE_EDITOR


def test_update_trip_settings_persists_changes(db_session):
    trip = TripFactory(event_categories=["travel"], calendar_auto_sync=False)

    updated = update_trip_settings(
        db_session,
        trip,
        event_categories=["meal", "stay"],
        calendar_auto_sync=True,
    )

    assert updated.event_categories == ["meal", "stay"]
    assert updated.calendar_auto_sync is True
