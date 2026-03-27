from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
import httpx
from app.core.config import settings


GOOGLE_CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar"


def build_google_login_url() -> str:
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_oauth_redirect_uri,
        "response_type": "code",
        "scope": f"openid email profile {GOOGLE_CALENDAR_SCOPE}",
        "access_type": "offline",
        "prompt": "consent",
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)


async def exchange_code_for_user(code: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_oauth_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        token_response.raise_for_status()
        token_payload = token_response.json()
        access_token = token_payload["access_token"]
        refresh_token = token_payload.get("refresh_token")
        expires_in = int(token_payload.get("expires_in", 3600))
        userinfo_response = await client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        userinfo_response.raise_for_status()
        payload = userinfo_response.json()
        payload["access_token"] = access_token
        payload["refresh_token"] = refresh_token
        payload["token_expires_at"] = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        return payload


async def refresh_google_access_token(refresh_token: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        token_response.raise_for_status()
        token_payload = token_response.json()
        expires_in = int(token_payload.get("expires_in", 3600))
        return {
            "access_token": token_payload["access_token"],
            "token_expires_at": datetime.now(timezone.utc) + timedelta(seconds=expires_in),
        }
