import { AppShell } from "@/components/shared/app-shell";
import { UserMenu } from "@/components/auth/user-menu";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CreateTripForm } from "@/components/trips/create-trip-form";
import { listTrips } from "@/features/trips/api";
import { getIntegrationHealth } from "@/features/integrations/api";
import { TripsGrid } from "@/components/trips/trips-grid";
import { getCurrentUser } from "@/lib/auth/session";

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-border bg-muted px-4 py-3">
      <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</p>
      <p className="mt-1 text-sm font-medium">{value}</p>
    </div>
  );
}

export default async function DashboardPage() {
  const user = await getCurrentUser();
  const [trips, integrations] = await Promise.allSettled([listTrips(), getIntegrationHealth()]);

  return (
    <AppShell
      eyebrow="Trips Planner"
      title="Dashboard"
      description="Your personal travel assistant. Plan your trips, explore new destinations, and manage your travel itineraries with ease."
      actions={user ? <UserMenu user={user} /> : null}
    >
      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <CreateTripForm />
        <Card>
          <CardHeader>
            <CardTitle>Explore</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Badge>Soon!</Badge>
            <p className="text-sm leading-6 text-muted-foreground">
              Explore trips, destinations and more!
            </p>
            {/* {integrations.status === "fulfilled" ? (
              <div className="grid gap-3 text-sm md:grid-cols-3">
                <Metric label="Auth" value={integrations.value.auth} />
                <Metric label="Calendar" value={integrations.value.calendar} />
                <Metric label="Maps" value={integrations.value.maps} />
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Integration status unavailable until the backend is running.</p>
            )} */}
          </CardContent>
        </Card>
      </div>

      {trips.status === "fulfilled" ? (
        <TripsGrid trips={trips.value} />
      ) : (
        <Card>
          <CardHeader><CardTitle>No trips yet</CardTitle></CardHeader>
          <CardContent><p className="text-sm leading-6 text-muted-foreground">Start adding trips so you can explore the world!</p></CardContent>
        </Card>
      )}
    </AppShell>
  );
}
