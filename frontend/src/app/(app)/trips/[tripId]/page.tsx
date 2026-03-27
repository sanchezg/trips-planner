import Link from "next/link";
import { AppShell } from "@/components/shared/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getTrip } from "@/features/trips/api";

export default async function TripDetailsPage({ params }: { params: Promise<{ tripId: string }> }) {
  const { tripId } = await params;
  const trip = await getTrip(tripId).catch(() => null);

  return (
    <AppShell eyebrow="Trip detail" title={trip?.name ?? "Trip"} description="Trip details are composed from backend resources and are ready to expand into itinerary, expenses, and collaboration workflows.">
      <Card>
        <CardHeader><CardTitle>{trip?.name ?? "Unknown trip"}</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm leading-6 text-muted-foreground">{trip?.description ?? "No description available."}</p>
          <div className="flex flex-wrap gap-3">
            <Link href={"/trips/" + tripId + "/itinerary"}><Button variant="outline">Itinerary</Button></Link>
            <Link href={"/trips/" + tripId + "/expenses"}><Button variant="outline">Expenses</Button></Link>
            <Link href={"/trips/" + tripId + "/settings"}><Button variant="outline">Settings</Button></Link>
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
