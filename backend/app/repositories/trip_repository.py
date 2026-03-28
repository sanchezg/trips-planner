from datetime import date
import secrets
import string

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.models.trip import Trip
from app.db.models.trip_member import TripMember
from app.db.models.trip_share_code import TripShareCode

TRIP_ROLE_OWNER = "owner"
TRIP_ROLE_EDITOR = "editor"
TRIP_ROLE_VIEWER = "viewer"
TRIP_ROLE_ORDER = {
    TRIP_ROLE_VIEWER: 1,
    TRIP_ROLE_EDITOR: 2,
    TRIP_ROLE_OWNER: 3,
}
TRIP_EDIT_ROLES = {TRIP_ROLE_OWNER, TRIP_ROLE_EDITOR}
_SHARE_CODE_ALPHABET = string.ascii_uppercase + string.digits


def _shared_trip_window_filter():
    return or_(Trip.ends_at.is_(None), Trip.ends_at >= date.today())


def _base_user_trip_query(db: Session, user_id: str):
    membership_exists = (
        db.query(TripMember.id)
        .filter(
            TripMember.trip_id == Trip.id,
            TripMember.user_id == user_id,
            _shared_trip_window_filter(),
        )
        .exists()
    )
    return db.query(Trip).filter(or_(Trip.owner_id == user_id, membership_exists))


def list_for_user(db: Session, user_id: str) -> list[Trip]:
    return _base_user_trip_query(db, user_id).order_by(Trip.starts_at.asc()).all()


def get_for_user(db: Session, trip_id: str, user_id: str) -> Trip | None:
    return _base_user_trip_query(db, user_id).filter(Trip.id == trip_id).first()


def get_owned_trip(db: Session, trip_id: str, user_id: str) -> Trip | None:
    return db.query(Trip).filter(Trip.id == trip_id, Trip.owner_id == user_id).first()


def get_trip_role(db: Session, trip: Trip, user_id: str) -> str | None:
    if trip.owner_id == user_id:
        return TRIP_ROLE_OWNER

    if trip.ends_at is not None and trip.ends_at < date.today():
        return None

    membership = (
        db.query(TripMember)
        .filter(TripMember.trip_id == trip.id, TripMember.user_id == user_id)
        .first()
    )
    return membership.role if membership else None


def has_required_role(role: str | None, minimum_role: str) -> bool:
    if role is None:
        return False
    return TRIP_ROLE_ORDER[role] >= TRIP_ROLE_ORDER[minimum_role]


def get_trip_for_min_role(db: Session, trip_id: str, user_id: str, minimum_role: str) -> Trip | None:
    trip = get_for_user(db, trip_id, user_id)
    if not trip:
        return None
    role = get_trip_role(db, trip, user_id)
    if not has_required_role(role, minimum_role):
        return None
    return trip


def create_trip(db: Session, trip: Trip) -> Trip:
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


def update_trip_settings(db: Session, trip: Trip, *, event_categories: list[str], calendar_auto_sync: bool) -> Trip:
    trip.event_categories = event_categories
    trip.calendar_auto_sync = calendar_auto_sync
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


def create_share_code(db: Session, trip: Trip, role: str) -> TripShareCode:
    existing = (
        db.query(TripShareCode)
        .filter(TripShareCode.trip_id == trip.id, TripShareCode.role == role)
        .first()
    )
    if existing:
        return existing

    while True:
        share_code = "".join(secrets.choice(_SHARE_CODE_ALPHABET) for _ in range(8))
        existing_code = db.query(TripShareCode).filter(TripShareCode.code == share_code).first()
        if not existing_code:
            record = TripShareCode(trip_id=trip.id, code=share_code, role=role)
            db.add(record)
            db.commit()
            db.refresh(record)
            return record


def join_trip_by_code(db: Session, *, code: str, user_id: str) -> Trip | None:
    normalized = code.strip().upper()
    share_link = (
        db.query(TripShareCode)
        .join(Trip, Trip.id == TripShareCode.trip_id)
        .filter(TripShareCode.code == normalized)
        .first()
    )
    if not share_link:
        return None

    trip = db.query(Trip).filter(Trip.id == share_link.trip_id).first()
    if not trip:
        return None

    if trip.owner_id == user_id:
        return trip

    existing = (
        db.query(TripMember)
        .filter(TripMember.trip_id == trip.id, TripMember.user_id == user_id)
        .first()
    )
    if not existing:
        membership = TripMember(trip_id=trip.id, user_id=user_id, role=share_link.role)
        db.add(membership)
        db.commit()
        return trip

    if TRIP_ROLE_ORDER[share_link.role] > TRIP_ROLE_ORDER[existing.role]:
        existing.role = share_link.role
        db.add(existing)
        db.commit()

    return trip
