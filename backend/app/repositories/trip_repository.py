from datetime import datetime
import secrets
import string

from sqlalchemy import exists, or_
from sqlalchemy.orm import Session
from app.db.models.trip import Trip
from app.db.models.trip_member import TripMember


_SHARE_CODE_ALPHABET = string.ascii_uppercase + string.digits



def _base_user_trip_query(db: Session, user_id: str):
    membership_exists = (
        db.query(TripMember.id)
        .filter(TripMember.trip_id == Trip.id, TripMember.user_id == user_id, Trip.ends_at >= datetime.today())
        .exists()
    )
    return db.query(Trip).filter(or_(Trip.owner_id == user_id, membership_exists))



def list_for_user(db: Session, user_id: str) -> list[Trip]:
    return (
        _base_user_trip_query(db, user_id)
        .order_by(Trip.starts_at.asc())
        .all()
    )



def get_for_user(db: Session, trip_id: str, user_id: str) -> Trip | None:
    return _base_user_trip_query(db, user_id).filter(Trip.id == trip_id).first()



def get_owned_trip(db: Session, trip_id: str, user_id: str) -> Trip | None:
    return db.query(Trip).filter(Trip.id == trip_id, Trip.owner_id == user_id).first()



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



def create_share_code(db: Session, trip: Trip) -> Trip:
    while True:
        share_code = ''.join(secrets.choice(_SHARE_CODE_ALPHABET) for _ in range(8))
        existing = db.query(Trip).filter(Trip.share_code == share_code).first()
        if not existing:
            trip.share_code = share_code
            db.add(trip)
            db.commit()
            db.refresh(trip)
            return trip



def join_trip_by_code(db: Session, *, code: str, user_id: str) -> Trip | None:
    normalized = code.strip().upper()
    trip = db.query(Trip).filter(Trip.share_code == normalized).first()
    if not trip:
        return None

    if trip.owner_id == user_id:
        return trip

    existing = db.query(TripMember).filter(TripMember.trip_id == trip.id, TripMember.user_id == user_id).first()
    if not existing:
        membership = TripMember(trip_id=trip.id, user_id=user_id, role='viewer')
        db.add(membership)
        db.commit()
    return trip
