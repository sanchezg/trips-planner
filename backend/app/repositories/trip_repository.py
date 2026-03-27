from datetime import datetime

from sqlalchemy.orm import Session
from app.db.models.trip import Trip


def list_for_user(db: Session, user_id: str) -> list[Trip]:
    return db.query(Trip).filter(Trip.owner_id == user_id, Trip.ends_at >= datetime.today()).order_by(Trip.starts_at.asc()).all()


def get_for_user(db: Session, trip_id: str, user_id: str) -> Trip | None:
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
