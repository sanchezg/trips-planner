from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.destination import Destination
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.repositories.trip_repository import TRIP_ROLE_EDITOR, get_for_user, get_trip_for_min_role
from app.schemas.destination import DestinationCreate, DestinationRead

router = APIRouter()


@router.get("", response_model=list[DestinationRead])
def list_destinations(trip_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = get_for_user(db, trip_id, current_user.id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db.query(Destination).filter(Destination.trip_id == trip_id).order_by(Destination.sort_order.asc()).all()


@router.post("", response_model=DestinationRead)
def create_destination(payload: DestinationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = get_trip_for_min_role(db, payload.trip_id, current_user.id, TRIP_ROLE_EDITOR)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    destination = Destination(**payload.model_dump())
    db.add(destination)
    db.commit()
    db.refresh(destination)
    return destination
