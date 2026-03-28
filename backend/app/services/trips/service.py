from app.db.models.trip import Trip
from app.repositories.trip_repository import TRIP_EDIT_ROLES, TRIP_ROLE_OWNER


def build_trip(*, owner_id: str, name: str, description: str | None, starts_at, ends_at, visibility: str) -> Trip:
    return Trip(owner_id=owner_id, name=name, description=description, starts_at=starts_at, ends_at=ends_at, visibility=visibility)


def build_trip_response(trip: Trip, membership_role: str) -> dict:
    return {
        "id": trip.id,
        "name": trip.name,
        "description": trip.description,
        "starts_at": trip.starts_at,
        "ends_at": trip.ends_at,
        "visibility": trip.visibility,
        "event_categories": trip.event_categories,
        "calendar_auto_sync": trip.calendar_auto_sync,
        "is_owner": membership_role == TRIP_ROLE_OWNER,
        "membership_role": membership_role,
        "can_edit": membership_role in TRIP_EDIT_ROLES,
        "can_manage_sharing": membership_role == TRIP_ROLE_OWNER,
    }
