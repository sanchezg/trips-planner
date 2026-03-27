from fastapi import APIRouter
from app.services.google_calendar.service import export_trip_events

router = APIRouter()


@router.post("/export/{trip_id}")
async def export_calendar(trip_id: str) -> dict:
    return await export_trip_events(trip_id)
