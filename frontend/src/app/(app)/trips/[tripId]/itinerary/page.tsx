import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function TripItineraryPage({ params }: { params: Promise<{ tripId: string }> }) {
  const { tripId } = await params;
  return (
    <AppShell eyebrow="Events" title="Itinerary" description={"This view is reserved for event CRUD, destination ordering, and non-blocking conflict detection for trip " + tripId + "."}>
      <Card>
        <CardHeader><CardTitle>Backend-driven itinerary module</CardTitle></CardHeader>
        <CardContent><p className="text-sm leading-6 text-muted-foreground">The FastAPI backend owns events, conflict warnings, route estimates, and future calendar synchronization.</p></CardContent>
      </Card>
    </AppShell>
  );
}
