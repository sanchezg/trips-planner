import { AppShell } from "@/components/shared/app-shell";
import { TripsGrid } from "@/components/trips/trips-grid";
import { listTrips } from "@/features/trips/api";

export default async function TripsPage() {
  const trips = await listTrips().catch(() => []);
  return (
    <AppShell eyebrow="Trips" title="All trips" description="Trips are fetched from the FastAPI backend through a typed client wrapper, keeping the frontend independent from persistence and business rules.">
      <TripsGrid trips={trips} />
    </AppShell>
  );
}
