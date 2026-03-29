from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import factory

from app.db.models.trip import Trip
from app.db.models.trip_member import TripMember
from app.db.models.trip_share_code import TripShareCode
from tests.factories.base import SQLAlchemySessionFactory
from tests.factories.user import UserFactory


class TripFactory(SQLAlchemySessionFactory):
    class Meta:
        model = Trip

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    owner = factory.SubFactory(UserFactory)
    owner_id = factory.SelfAttribute("owner.id")
    name = factory.Sequence(lambda n: f"Trip {n}")
    description = factory.Faker("sentence")
    starts_at = factory.LazyFunction(lambda: datetime.now(timezone.utc) + timedelta(days=1))
    ends_at = factory.LazyAttribute(lambda obj: obj.starts_at + timedelta(days=4))
    flight_number = None
    airport = None
    visibility = "private"
    share_code = None
    event_categories = ["transit", "travel", "stay", "entertainment", "meal"]
    calendar_auto_sync = False


class TripMemberFactory(SQLAlchemySessionFactory):
    class Meta:
        model = TripMember

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    trip_id = factory.LazyFunction(lambda: TripFactory().id)
    user_id = factory.LazyFunction(lambda: UserFactory().id)
    role = "viewer"

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        trip = kwargs.pop("trip", None)
        user = kwargs.pop("user", None)
        if trip is not None:
            kwargs["trip_id"] = trip.id
        if user is not None:
            kwargs["user_id"] = user.id
        return super()._adjust_kwargs(**kwargs)


class TripShareCodeFactory(SQLAlchemySessionFactory):
    class Meta:
        model = TripShareCode

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    trip_id = factory.LazyFunction(lambda: TripFactory().id)
    code = factory.Sequence(lambda n: f"SHARE{n:03d}")
    role = "viewer"

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        trip = kwargs.pop("trip", None)
        if trip is not None:
            kwargs["trip_id"] = trip.id
        return super()._adjust_kwargs(**kwargs)
