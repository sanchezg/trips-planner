from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.repositories.trip_repository import create_trip, get_for_user, list_for_user
from app.schemas.trip import TripCreate, TripRead
from app.services.trips.service import build_trip

router = APIRouter()


@router.get("", response_model=list[TripRead])
def get_trips(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_for_user(db, current_user.id)


@router.post("", response_model=TripRead)
def post_trip(payload: TripCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = build_trip(
        owner_id=current_user.id,
        name=payload.name,
        description=payload.description,
        starts_at=payload.startsAt,
        ends_at=payload.endsAt,
        visibility=payload.visibility,
    )
    return create_trip(db, trip)


@router.get("/{trip_id}", response_model=TripRead)
def get_trip(trip_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = get_for_user(db, trip_id, current_user.id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip
