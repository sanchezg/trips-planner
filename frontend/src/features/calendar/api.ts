import { apiFetch } from '@/lib/api-client';

export type CalendarSyncResponse = {
  status: string;
  trip_id: string;
  calendar_id: string;
  events_synced: number;
  message: string;
};

export async function syncTripToGoogleCalendar(tripId: string) {
  return apiFetch<CalendarSyncResponse>(`/api/routes/calendar/export/${tripId}`, {
    method: 'POST'
  });
}
