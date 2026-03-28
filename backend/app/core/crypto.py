from base64 import urlsafe_b64encode
from functools import lru_cache
from hashlib import sha256

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

_ENCRYPTED_PREFIX = "enc::"


@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    key_material = sha256(settings.resolved_token_encryption_secret.encode("utf-8")).digest()
    return Fernet(urlsafe_b64encode(key_material))


def encrypt_secret(value: str | None) -> str | None:
    if not value:
        return None
    encrypted = _get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")
    return _ENCRYPTED_PREFIX + encrypted


def decrypt_secret(value: str | None) -> str | None:
    if not value:
        return None
    if not value.startswith(_ENCRYPTED_PREFIX):
        return value

    token = value.removeprefix(_ENCRYPTED_PREFIX).encode("utf-8")
    try:
        return _get_fernet().decrypt(token).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Unable to decrypt stored secret") from exc
