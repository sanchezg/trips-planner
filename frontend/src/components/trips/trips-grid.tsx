import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle, CardSubTitle } from "@/components/ui/card";
import type { TripSummary } from "@/features/trips/api";

export function TripsGrid({ trips }: { trips: TripSummary[] }) {
  return (
    <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
      {trips.map((trip) => (
        <Link href={"/trips/" + trip.id} key={trip.id}>
          <Card className="h-full transition hover:-translate-y-0.5 hover:border-primary">
            <CardHeader>
              <CardTitle>{trip.name}</CardTitle>
              <CardSubTitle>{trip.starts_at} - {trip.ends_at}</CardSubTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-6 text-muted-foreground">{trip.description ?? "No description yet."}</p>
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
