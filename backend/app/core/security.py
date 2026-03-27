from itsdangerous import BadSignature, URLSafeSerializer
from app.core.config import settings

serializer = URLSafeSerializer(settings.session_secret, salt="trip-session")


def create_session_token(payload: dict[str, str]) -> str:
    return serializer.dumps(payload)


def decode_session_token(token: str) -> dict[str, str] | None:
    try:
        data = serializer.loads(token)
        return data if isinstance(data, dict) else None
    except BadSignature:
        return None
