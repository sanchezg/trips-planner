import { apiFetch } from "@/lib/api-client";
import type { TripCreateInput } from "@/lib/validations/trips";
import type { TripSettingsInput } from "@/lib/validations/trip-settings";

export type TripSummary = {
  id: string;
  name: string;
  description: string | null;
  starts_at: string | null;
  ends_at: string | null;
  visibility: string;
  share_code: string | null;
  event_categories: string[];
  calendar_auto_sync: boolean;
  is_owner: boolean;
};

export type TripSettings = {
  event_categories: string[];
  calendar_auto_sync: boolean;
};

export type TripShareCode = {
  share_code: string;
};

export async function listTrips() {
  return apiFetch<TripSummary[]>("/api/routes/trips");
}

export async function getTrip(tripId: string) {
  return apiFetch<TripSummary>("/api/routes/trips/" + tripId);
}

export async function createTrip(payload: TripCreateInput) {
  return apiFetch<TripSummary>("/api/routes/trips", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function joinTrip(code: string) {
  return apiFetch<TripSummary>("/api/routes/trips/join", {
    method: 'POST',
    body: JSON.stringify({ code })
  });
}

export async function createTripShareCode(tripId: string) {
  return apiFetch<TripShareCode>(`/api/routes/trips/${tripId}/share-code`, {
    method: 'POST'
  });
}

export async function getTripSettings(tripId: string) {
  return apiFetch<TripSettings>("/api/routes/trips/" + tripId + "/settings");
}

export async function updateTripSettings(tripId: string, payload: TripSettingsInput) {
  return apiFetch<TripSettings>("/api/routes/trips/" + tripId + "/settings", {
    method: "PATCH",
    body: JSON.stringify({
      event_categories: payload.eventCategories,
      calendar_auto_sync: payload.calendarAutoSync
    })
  });
}
