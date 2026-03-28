from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.user import User
from app.dependencies.db import get_db
from app.repositories.session_repository import get_active_session


def get_current_user(
    trip_session: str | None = Cookie(default=None, alias=settings.session_cookie_name),
    db: Session = Depends(get_db),
) -> User:
    if not trip_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing session")

    session = get_active_session(db, trip_session)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    user = db.get(User, session.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
