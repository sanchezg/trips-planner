from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import decode_session_token
from app.db.models.user import User
from app.dependencies.db import get_db


def get_current_user(trip_session: str | None = Cookie(default=None), db: Session = Depends(get_db)) -> User:
    if not trip_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing session")

    payload = decode_session_token(trip_session)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    user = db.get(User, payload["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
