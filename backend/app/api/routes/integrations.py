from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/status")
def integration_status() -> dict[str, str]:
    return {
        "auth": "configured" if settings.google_client_id else "missing Google OAuth config",
        "calendar": "ready for Google Calendar wiring",
        "maps": "configured" if settings.google_maps_api_key else "missing Maps API key",
    }
