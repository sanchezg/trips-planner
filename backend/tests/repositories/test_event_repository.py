from __future__ import annotations

from datetime import timedelta

from app.repositories.event_repository import list_for_trip
from tests.factories.event import EventFactory
from tests.factories.trip import TripFactory


def test_list_for_trip_returns_events_sorted_by_start_time(db_session):
    trip = TripFactory()
    late_event = EventFactory(trip=trip, title="Late", starts_at=trip.starts_at + timedelta(hours=5), ends_at=trip.starts_at + timedelta(hours=6))
    early_event = EventFactory(trip=trip, title="Early", starts_at=trip.starts_at + timedelta(hours=1), ends_at=trip.starts_at + timedelta(hours=2))

    events = list_for_trip(db_session, trip.id)

    assert [event.id for event in events] == [early_event.id, late_event.id]
