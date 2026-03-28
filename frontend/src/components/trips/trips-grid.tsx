import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle, CardSubTitle } from "@/components/ui/card";
import type { TripSummary } from "@/features/trips/api";

const tripDateFormatter = new Intl.DateTimeFormat("en", {
  month: "short",
  day: "numeric",
  year: "numeric",
  hour: "numeric",
  minute: "2-digit"
});

function formatTripWindow(trip: TripSummary) {
  if (!trip.starts_at && !trip.ends_at) {
    return "Dates to be confirmed";
  }

  const start = trip.starts_at ? tripDateFormatter.format(new Date(trip.starts_at)) : "TBD";
  const end = trip.ends_at ? tripDateFormatter.format(new Date(trip.ends_at)) : "TBD";
  return `${start} - ${end}`;
}

export function TripsGrid({ trips }: { trips: TripSummary[] }) {
  return (
    <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
      {trips.map((trip) => (
        <Link href={"/trips/" + trip.id} key={trip.id}>
          <Card className="h-full transition hover:-translate-y-0.5 hover:border-primary">
            <CardHeader>
              <CardTitle>{trip.name}</CardTitle>
              <CardSubTitle>{formatTripWindow(trip)}</CardSubTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-6 text-muted-foreground">{trip.description ?? "No description yet."}</p>
              {trip.flight_number || trip.airport ? (
                <p className="mt-3 text-sm text-muted-foreground">{[trip.flight_number, trip.airport].filter(Boolean).join(" · ")}</p>
              ) : null}
              <p className="mt-4 text-xs uppercase tracking-[0.2em] text-primary">
                {trip.is_owner ? trip.visibility : `${trip.membership_role} access`}
              </p>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}
