import { apiFetch } from "@/lib/api-client";
import type { TripCreateInput } from "@/lib/validations/trips";
import type { TripSettingsInput } from "@/lib/validations/trip-settings";

export type TripRole = "owner" | "editor" | "viewer";
export type ShareableTripRole = Exclude<TripRole, "owner">;

export type TripSummary = {
  id: string;
  name: string;
  description: string | null;
  starts_at: string | null;
  ends_at: string | null;
  flight_number: string | null;
  airport: string | null;
  visibility: string;
  event_categories: string[];
  calendar_auto_sync: boolean;
  is_owner: boolean;
  membership_role: TripRole;
  can_edit: boolean;
  can_manage_sharing: boolean;
};

export type TripSettings = {
  event_categories: string[];
  calendar_auto_sync: boolean;
};

export type TripShareCode = {
  share_code: string;
  role: ShareableTripRole;
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
    body: JSON.stringify({
      ...payload,
      startsAt: payload.startsAt ? new Date(payload.startsAt).toISOString() : undefined,
      endsAt: payload.endsAt ? new Date(payload.endsAt).toISOString() : undefined,
      flightNumber: payload.flightNumber || undefined,
      airport: payload.airport || undefined,
    })
  });
}

export async function joinTrip(code: string) {
  return apiFetch<TripSummary>("/api/routes/trips/join", {
    method: "POST",
    body: JSON.stringify({ code })
  });
}

export async function createTripShareCode(tripId: string, role: ShareableTripRole) {
  return apiFetch<TripShareCode>(`/api/routes/trips/${tripId}/share-code`, {
    method: "POST",
    body: JSON.stringify({ role })
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
