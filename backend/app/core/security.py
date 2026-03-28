import hashlib
import secrets

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import settings

oauth_state_serializer = URLSafeTimedSerializer(settings.session_secret, salt="trip-oauth-state")


def create_session_token() -> str:
    return secrets.token_urlsafe(48)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_oauth_state() -> tuple[str, str]:
    state = secrets.token_urlsafe(32)
    cookie_value = oauth_state_serializer.dumps({"state": state})
    return state, cookie_value


def validate_oauth_state(cookie_value: str | None, state: str | None) -> bool:
    if not cookie_value or not state:
        return False

    try:
        payload = oauth_state_serializer.loads(cookie_value, max_age=settings.oauth_state_max_age_seconds)
    except (BadSignature, SignatureExpired):
        return False

    return payload.get("state") == state
