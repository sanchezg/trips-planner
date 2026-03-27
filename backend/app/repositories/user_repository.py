from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.user import User


def get_by_google_sub(db: Session, google_sub: str) -> User | None:
    return db.query(User).filter(User.google_sub == google_sub).first()


def get_or_create_google_user(
    db: Session,
    *,
    email: str,
    name: str | None,
    avatar_url: str | None,
    google_sub: str,
    google_access_token: str | None,
    google_refresh_token: str | None,
    google_token_expires_at: datetime | None,
) -> User:
    user = get_by_google_sub(db, google_sub)
    if user:
        user.email = email
        user.name = name
        user.avatar_url = avatar_url
        user.google_access_token = google_access_token
        if google_refresh_token:
            user.google_refresh_token = google_refresh_token
        user.google_token_expires_at = google_token_expires_at
    else:
        user = User(
            email=email,
            name=name,
            avatar_url=avatar_url,
            google_sub=google_sub,
            google_access_token=google_access_token,
            google_refresh_token=google_refresh_token,
            google_token_expires_at=google_token_expires_at,
        )
        db.add(user)
    db.commit()
    db.refresh(user)
    return user
