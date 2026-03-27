from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.repositories.trip_repository import create_trip, get_for_user, list_for_user, update_trip_settings
from app.schemas.trip import TripCreate, TripRead, TripSettingsRead, TripSettingsUpdate
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


@router.get("/{trip_id}/settings", response_model=TripSettingsRead)
def get_trip_settings(trip_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = get_for_user(db, trip_id, current_user.id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.patch("/{trip_id}/settings", response_model=TripSettingsRead)
def patch_trip_settings(trip_id: str, payload: TripSettingsUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = get_for_user(db, trip_id, current_user.id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    normalized_categories = []
    seen = set()
    for category in payload.event_categories:
        normalized = category.strip().lower()
        if normalized and normalized not in seen:
            normalized_categories.append(normalized)
            seen.add(normalized)

    if not normalized_categories:
        raise HTTPException(status_code=422, detail="At least one event category is required")

    return update_trip_settings(
        db,
        trip,
        event_categories=normalized_categories,
        calendar_auto_sync=payload.calendar_auto_sync,
    )
