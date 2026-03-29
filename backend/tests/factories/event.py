from __future__ import annotations

import uuid
from datetime import timedelta

import factory

from app.db.models.event import Event
from tests.factories.base import SQLAlchemySessionFactory
from tests.factories.trip import TripFactory


class EventFactory(SQLAlchemySessionFactory):
    class Meta:
        model = Event

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    trip_id = factory.LazyFunction(lambda: TripFactory().id)
    destination_id = None
    title = factory.Sequence(lambda n: f"Event {n}")
    category = "travel"
    address = factory.Faker("address")
    starts_at = factory.LazyFunction(lambda: TripFactory().starts_at)
    ends_at = factory.LazyAttribute(lambda obj: obj.starts_at + timedelta(hours=2))
    notes = factory.Faker("sentence")

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        trip = kwargs.pop("trip", None)
        if trip is not None:
            kwargs["trip_id"] = trip.id
            kwargs.setdefault("starts_at", trip.starts_at)
            kwargs.setdefault("ends_at", trip.starts_at + timedelta(hours=2))
        return super()._adjust_kwargs(**kwargs)
