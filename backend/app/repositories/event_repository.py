from sqlalchemy.orm import Session
from app.db.models.event import Event


def list_for_trip(db: Session, trip_id: str) -> list[Event]:
    return db.query(Event).filter(Event.trip_id == trip_id).order_by(Event.starts_at.asc()).all()
