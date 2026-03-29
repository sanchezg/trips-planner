import hashlib
import secrets

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import settings

oauth_state_serializer = URLSafeTimedSerializer(settings.session_secret, salt="trip-oauth-state")


def create_session_token() -> str:
    return secrets.token_urlsafe(48)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_oauth_state(next_path: str | None = None) -> tuple[str, str]:
    state = secrets.token_urlsafe(32)
    payload = {"state": state}
    if next_path:
        payload["next_path"] = next_path
    cookie_value = oauth_state_serializer.dumps(payload)
    return state, cookie_value


def read_oauth_state(cookie_value: str | None, state: str | None) -> dict[str, str] | None:
    if not cookie_value or not state:
        return None

    try:
        payload = oauth_state_serializer.loads(cookie_value, max_age=settings.oauth_state_max_age_seconds)
    except (BadSignature, SignatureExpired):
        return None

    if payload.get("state") != state:
        return None

    return payload if isinstance(payload, dict) else None
