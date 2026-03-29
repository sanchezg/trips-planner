from __future__ import annotations

from tests.factories.event import EventFactory
from tests.factories.trip import TripFactory


def test_export_calendar_delegates_to_google_calendar_service(authenticated_client, mocker):
    client, user = authenticated_client
    trip = TripFactory(owner=user)
    EventFactory(trip=trip, title="Flight")
    mocked_export = mocker.patch(
        "app.api.routes.calendar.export_trip_events",
        return_value={
            "status": "synced",
            "trip_id": trip.id,
            "calendar_id": "calendar-123",
            "events_synced": 1,
            "message": "Synced.",
        },
    )

    response = client.post(f"/api/routes/calendar/export/{trip.id}")

    assert response.status_code == 200
    assert response.json()["trip_id"] == trip.id
    mocked_export.assert_called_once()
