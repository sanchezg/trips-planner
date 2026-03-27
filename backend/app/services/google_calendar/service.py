async def export_trip_events(trip_id: str) -> dict:
    return {
        "status": "pending",
        "trip_id": trip_id,
        "message": "Hook Google Calendar export here.",
    }
