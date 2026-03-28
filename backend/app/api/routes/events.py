from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.event import Event
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.repositories.trip_repository import TRIP_ROLE_EDITOR, get_for_user, get_trip_for_min_role
from app.schemas.event import EventCreate, EventMutationResult, EventRead, EventUpdate
from app.services.conflict_detection.service import detect_conflicts

router = APIRouter()


def _get_event_for_edit(db: Session, event_id: str, user_id: str) -> Event | None:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None

    trip = get_trip_for_min_role(db, event.trip_id, user_id, TRIP_ROLE_EDITOR)
    if not trip:
        return None

    return event


def _build_warnings(db: Session, payload: EventCreate | EventUpdate, ignore_event_id: str | None = None) -> list[str]:
    query = db.query(Event).filter(Event.trip_id == payload.trip_id)
    if ignore_event_id:
        query = query.filter(Event.id != ignore_event_id)

    existing = query.order_by(Event.starts_at.asc()).all()
    return detect_conflicts([
        *[
            {"title": event.title, "starts_at": event.starts_at, "ends_at": event.ends_at}
            for event in existing
        ],
        {"title": payload.title, "starts_at": payload.starts_at, "ends_at": payload.ends_at},
    ])


@router.get("", response_model=list[EventRead])
def list_events(trip_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = get_for_user(db, trip_id, current_user.id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    return db.query(Event).filter(Event.trip_id == trip_id).order_by(Event.starts_at.asc()).all()


@router.post("", response_model=EventMutationResult)
def create_event(payload: EventCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = get_trip_for_min_role(db, payload.trip_id, current_user.id, TRIP_ROLE_EDITOR)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    warnings = _build_warnings(db, payload)
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return EventMutationResult(event=EventRead.model_validate(event), warnings=warnings)


@router.put("/{event_id}", response_model=EventMutationResult)
def update_event(event_id: str, payload: EventUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = get_trip_for_min_role(db, payload.trip_id, current_user.id, TRIP_ROLE_EDITOR)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    event = _get_event_for_edit(db, event_id, current_user.id)
    if not event or event.trip_id != payload.trip_id:
        raise HTTPException(status_code=404, detail="Event not found")

    warnings = _build_warnings(db, payload, ignore_event_id=event.id)
    for field, value in payload.model_dump().items():
        setattr(event, field, value)

    db.add(event)
    db.commit()
    db.refresh(event)
    return EventMutationResult(event=EventRead.model_validate(event), warnings=warnings)


@router.delete("/{event_id}")
def delete_event(event_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    event = _get_event_for_edit(db, event_id, current_user.id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(event)
    db.commit()
    return {"ok": True}
