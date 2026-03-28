from datetime import datetime, timezone
from urllib.parse import quote
import uuid

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models.calendar import CalendarSync
from app.db.models.event import Event
from app.db.models.trip import Trip
from app.db.models.user import User
from app.services.auth.google_oauth import refresh_google_access_token


GOOGLE_CALENDAR_API = "https://www.googleapis.com/calendar/v3"


async def _ensure_access_token(db: Session, user: User) -> str:
    now = datetime.now(timezone.utc)
    expires_at = user.google_token_expires_at
    if user.google_access_token and (not expires_at or expires_at > now):
        return user.google_access_token

    if not user.google_refresh_token:
        raise HTTPException(status_code=400, detail="Google Calendar access is not connected for this account")

    refreshed = await refresh_google_access_token(user.google_refresh_token)
    user.google_access_token = refreshed["access_token"]
    user.google_token_expires_at = refreshed["token_expires_at"]
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.google_access_token


async def _google_request(method: str, path: str, access_token: str, *, json: dict | None = None) -> dict | list:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.request(
            method,
            GOOGLE_CALENDAR_API + path,
            headers={"Authorization": f"Bearer {access_token}"},
            json=json,
        )
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"Google Calendar API error: {response.text}")
        if response.content:
            return response.json()
        return {}


async def _ensure_trip_calendar(db: Session, access_token: str, trip: Trip) -> CalendarSync:
    sync = db.query(CalendarSync).filter(CalendarSync.trip_id == trip.id, CalendarSync.provider == "google").first()
    if sync and sync.external_calendar_id:
        await _google_request(
            "PATCH",
            f"/calendars/{quote(sync.external_calendar_id, safe='')}",
            access_token,
            json={
                "summary": trip.name,
                "description": trip.description or f"Trip plan for {trip.name}",
            },
        )
        return sync

    calendar = await _google_request(
        "POST",
        "/calendars",
        access_token,
        json={
            "summary": trip.name,
            "description": trip.description or f"Trip plan for {trip.name}",
        },
    )
    sync = sync or CalendarSync(id=str(uuid.uuid4()), trip_id=trip.id, provider="google")
    sync.external_calendar_id = calendar["id"]
    db.add(sync)
    db.commit()
    db.refresh(sync)
    return sync


async def _clear_calendar_events(access_token: str, calendar_id: str) -> None:
    events_payload = await _google_request(
        "GET",
        f"/calendars/{quote(calendar_id, safe='')}/events",
        access_token,
    )
    for item in events_payload.get("items", []):
        if item.get("status") == "cancelled":
            continue
        await _google_request(
            "DELETE",
            f"/calendars/{quote(calendar_id, safe='')}/events/{quote(item['id'], safe='')}",
            access_token,
        )


async def _create_calendar_events(access_token: str, calendar_id: str, trip: Trip, events: list[Event]) -> None:
    if trip.starts_at and trip.ends_at:
        trip_description_parts = [trip.description or f"Overview for {trip.name}"]
        if trip.flight_number:
            trip_description_parts.append(f"Flight: {trip.flight_number}")
        if trip.airport:
            trip_description_parts.append(f"Airport: {trip.airport}")

        await _google_request(
            "POST",
            f"/calendars/{quote(calendar_id, safe='')}/events",
            access_token,
            json={
                "summary": trip.name,
                "description": "\n".join(trip_description_parts),
                "location": trip.airport,
                "start": {"dateTime": trip.starts_at.astimezone(timezone.utc).isoformat()},
                "end": {"dateTime": trip.ends_at.astimezone(timezone.utc).isoformat()},
            },
        )

    for event in events:
        await _google_request(
            "POST",
            f"/calendars/{quote(calendar_id, safe='')}/events",
            access_token,
            json={
                "summary": event.title,
                "description": event.notes or trip.description or "Synced from Trips Planner",
                "location": event.address,
                "start": {"dateTime": event.starts_at.astimezone(timezone.utc).isoformat()},
                "end": {"dateTime": event.ends_at.astimezone(timezone.utc).isoformat()},
            },
        )


async def export_trip_events(db: Session, user: User, trip: Trip, events: list[Event]) -> dict:
    access_token = await _ensure_access_token(db, user)
    sync = await _ensure_trip_calendar(db, access_token, trip)
    await _clear_calendar_events(access_token, sync.external_calendar_id)
    await _create_calendar_events(access_token, sync.external_calendar_id, trip, events)
    sync.last_synced_at = datetime.now(timezone.utc)
    db.add(sync)
    db.commit()
    db.refresh(sync)
    return {
        "status": "synced",
        "trip_id": trip.id,
        "calendar_id": sync.external_calendar_id,
        "events_synced": len(events),
        "message": f"Synced {trip.name} and {len(events)} event(s) to Google Calendar.",
    }
