from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.event import Event
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.repositories.trip_repository import get_for_user
from app.services.google_calendar.service import export_trip_events

router = APIRouter()


@router.post("/export/{trip_id}")
async def export_calendar(trip_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    trip = get_for_user(db, trip_id, current_user.id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    events = db.query(Event).filter(Event.trip_id == trip_id).order_by(Event.starts_at.asc()).all()
    return await export_trip_events(db, current_user, trip, events)
