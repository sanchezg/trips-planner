import { apiFetch } from "@/lib/api-client";
import type { TripCreateInput } from "@/lib/validations/trips";

export type TripSummary = {
  id: string;
  name: string;
  description: string | null;
  starts_at: string | null;
  ends_at: string | null;
  visibility: string;
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
