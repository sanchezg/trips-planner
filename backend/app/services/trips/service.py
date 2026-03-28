from app.db.models.trip import Trip


def build_trip(*, owner_id: str, name: str, description: str | None, starts_at, ends_at, visibility: str) -> Trip:
    return Trip(owner_id=owner_id, name=name, description=description, starts_at=starts_at, ends_at=ends_at, visibility=visibility)


def build_trip_response(trip: Trip, user_id: str) -> dict:
    return {
        'id': trip.id,
        'name': trip.name,
        'description': trip.description,
        'starts_at': trip.starts_at,
        'ends_at': trip.ends_at,
        'visibility': trip.visibility,
        'share_code': trip.share_code,
        'event_categories': trip.event_categories,
        'calendar_auto_sync': trip.calendar_auto_sync,
        'is_owner': trip.owner_id == user_id,
    }
