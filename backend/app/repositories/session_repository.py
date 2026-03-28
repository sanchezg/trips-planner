from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_session_token
from app.db.models.user import User
from app.db.models.user_session import UserSession


SESSION_TOUCH_INTERVAL_SECONDS = 60 * 15


def create_user_session(db: Session, *, user: User, session_token: str) -> UserSession:
    now = datetime.now(timezone.utc)
    record = UserSession(
        user_id=user.id,
        token_hash=hash_session_token(session_token),
        expires_at=now + timedelta(seconds=settings.session_max_age_seconds),
        last_seen_at=now,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_active_session(db: Session, session_token: str) -> UserSession | None:
    now = datetime.now(timezone.utc)
    session = (
        db.query(UserSession)
        .filter(
            UserSession.token_hash == hash_session_token(session_token),
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > now,
        )
        .first()
    )
    if not session:
        return None

    if not session.last_seen_at or (now - session.last_seen_at).total_seconds() >= SESSION_TOUCH_INTERVAL_SECONDS:
        session.last_seen_at = now
        db.add(session)
        db.commit()
        db.refresh(session)

    return session


def revoke_session(db: Session, session_token: str) -> bool:
    session = get_active_session(db, session_token)
    if not session:
        return False

    session.revoked_at = datetime.now(timezone.utc)
    db.add(session)
    db.commit()
    return True
