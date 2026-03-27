from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models.event import Event
from app.db.models.trip import Trip
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.schemas.event import EventCreate, EventRead
from app.services.conflict_detection.service import detect_conflicts

router = APIRouter()


@router.get("", response_model=list[EventRead])
def list_events(trip_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.owner_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db.query(Event).filter(Event.trip_id == trip_id).order_by(Event.starts_at.asc()).all()


@router.post("")
def create_event(payload: EventCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == payload.trip_id, Trip.owner_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    existing = db.query(Event).filter(Event.trip_id == payload.trip_id).all()
    warnings = detect_conflicts([
        *[
            {"title": event.title, "starts_at": event.starts_at, "ends_at": event.ends_at}
            for event in existing
        ],
        {"title": payload.title, "starts_at": payload.starts_at, "ends_at": payload.ends_at},
    ])

    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"event": EventRead.model_validate(event), "warnings": warnings}
