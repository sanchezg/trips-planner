from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.repositories.trip_repository import (
    TRIP_ROLE_OWNER,
    create_share_code,
    create_trip,
    get_for_user,
    get_trip_for_min_role,
    get_trip_role,
    join_trip_by_code,
    list_for_user,
    update_trip_settings,
)
from app.schemas.trip import (
    TripCreate,
    TripJoin,
    TripRead,
    TripSettingsRead,
    TripSettingsUpdate,
    TripShareCodeCreate,
    TripShareCodeRead,
)
from app.services.trips.service import build_trip, build_trip_response

router = APIRouter()


@router.get("", response_model=list[TripRead])
def get_trips(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trips = list_for_user(db, current_user.id)
    return [
        build_trip_response(trip, get_trip_role(db, trip, current_user.id) or TRIP_ROLE_OWNER)
        for trip in trips
    ]


@router.post("", response_model=TripRead)
def post_trip(payload: TripCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = build_trip(
        owner_id=current_user.id,
        name=payload.name,
        description=payload.description,
        starts_at=payload.startsAt,
        ends_at=payload.endsAt,
        flight_number=payload.flightNumber,
        airport=payload.airport,
        visibility=payload.visibility,
    )
    trip = create_trip(db, trip)
    return build_trip_response(trip, TRIP_ROLE_OWNER)


@router.post("/join", response_model=TripRead)
def join_trip(payload: TripJoin, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = join_trip_by_code(db, code=payload.code, user_id=current_user.id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found for that code")
    role = get_trip_role(db, trip, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="Unable to join trip")
    return build_trip_response(trip, role)


@router.get("/{trip_id}", response_model=TripRead)
def get_trip(trip_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = get_for_user(db, trip_id, current_user.id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    role = get_trip_role(db, trip, current_user.id)
    if not role:
        raise HTTPException(status_code=404, detail="Trip not found")
    return build_trip_response(trip, role)


@router.post("/{trip_id}/share-code", response_model=TripShareCodeRead)
def post_trip_share_code(
    trip_id: str,
    payload: TripShareCodeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trip = get_trip_for_min_role(db, trip_id, current_user.id, TRIP_ROLE_OWNER)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    share_code = create_share_code(db, trip, payload.role)
    return TripShareCodeRead(share_code=share_code.code, role=share_code.role)


@router.get("/{trip_id}/settings", response_model=TripSettingsRead)
def get_trip_settings(trip_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = get_trip_for_min_role(db, trip_id, current_user.id, TRIP_ROLE_OWNER)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.patch("/{trip_id}/settings", response_model=TripSettingsRead)
def patch_trip_settings(trip_id: str, payload: TripSettingsUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = get_trip_for_min_role(db, trip_id, current_user.id, TRIP_ROLE_OWNER)
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
