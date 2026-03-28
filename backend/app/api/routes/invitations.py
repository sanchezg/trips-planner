import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.invitation import Invitation
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.repositories.trip_repository import TRIP_ROLE_OWNER, get_trip_for_min_role
from app.schemas.invitation import InvitationCreate, InvitationRead

router = APIRouter()


@router.get("", response_model=list[InvitationRead])
def list_invitations(trip_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = get_trip_for_min_role(db, trip_id, current_user.id, TRIP_ROLE_OWNER)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db.query(Invitation).filter(Invitation.trip_id == trip_id).order_by(Invitation.expires_at.desc()).all()


@router.post("", response_model=InvitationRead)
def create_invitation(payload: InvitationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = get_trip_for_min_role(db, payload.trip_id, current_user.id, TRIP_ROLE_OWNER)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    invitation = Invitation(
        trip_id=payload.trip_id,
        email=str(payload.email),
        role=payload.role,
        status="pending",
        token=secrets.token_urlsafe(24),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation
