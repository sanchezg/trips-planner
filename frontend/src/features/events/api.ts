import { apiFetch } from '@/lib/api-client';
import type { EventFormInput } from '@/lib/validations/events';

export type TripEvent = {
  id: string;
  trip_id: string;
  destination_id: string | null;
  title: string;
  category: string | null;
  address: string | null;
  starts_at: string;
  ends_at: string;
  notes: string | null;
};

export type EventMutationResponse = {
  event: TripEvent;
  warnings: string[];
};

function buildPayload(tripId: string, payload: EventFormInput) {
  return {
    trip_id: tripId,
    destination_id: payload.destinationId ?? null,
    title: payload.title,
    category: payload.category ?? null,
    address: payload.address ?? null,
    starts_at: new Date(payload.startsAt).toISOString(),
    ends_at: new Date(payload.endsAt).toISOString(),
    notes: payload.notes ?? null
  };
}

export async function listTripEvents(tripId: string) {
  return apiFetch<TripEvent[]>(`/api/routes/events?trip_id=${tripId}`);
}

export async function createTripEvent(tripId: string, payload: EventFormInput) {
  return apiFetch<EventMutationResponse>('/api/routes/events', {
    method: 'POST',
    body: JSON.stringify(buildPayload(tripId, payload))
  });
}

export async function updateTripEvent(eventId: string, tripId: string, payload: EventFormInput) {
  return apiFetch<EventMutationResponse>(`/api/routes/events/${eventId}`, {
    method: 'PUT',
    body: JSON.stringify(buildPayload(tripId, payload))
  });
}

export async function deleteTripEvent(eventId: string) {
  return apiFetch<{ ok: boolean }>(`/api/routes/events/${eventId}`, {
    method: 'DELETE'
  });
}
