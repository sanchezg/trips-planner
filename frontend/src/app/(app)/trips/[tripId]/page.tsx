import Link from 'next/link';
import { ShareTripButton } from '@/components/trips/share-trip-button';
import { SyncTripButton } from '@/components/trips/sync-trip-button';
import { TripEventsPlanner } from '@/components/trips/trip-events-planner';
import { AppShell } from '@/components/shared/app-shell';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { listTripEvents } from '@/features/events/api';
import { getTrip } from '@/features/trips/api';

export default async function TripDetailsPage({ params }: { params: Promise<{ tripId: string }> }) {
  const { tripId } = await params;
  const [trip, events] = await Promise.all([
    getTrip(tripId).catch(() => null),
    listTripEvents(tripId).catch(() => [])
  ]);

  return (
    <AppShell
      eyebrow='Trip detail'
      title={trip?.name ?? 'Trip'}
      description='Plan the trip day by day with a compact calendar, an itinerary list, and full event actions powered by the backend events module.'
    >
      <div className='space-y-6'>
        <div>
          <Link href='/dashboard'><Button variant='ghost'>Back to dashboard</Button></Link>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>{trip?.name ?? 'Unknown trip'}</CardTitle>
          </CardHeader>
          <CardContent className='space-y-4'>
            <p className='text-sm leading-6 text-muted-foreground'>{trip?.description ?? 'No description available.'}</p>
            <div className='flex flex-wrap items-start gap-3'>
              <Link href={'/trips/' + tripId + '/itinerary'}><Button variant='outline'>Itinerary</Button></Link>
              <Link href={'/trips/' + tripId + '/expenses'}><Button variant='outline'>Expenses</Button></Link>
              {trip?.is_owner ? <Link href={'/trips/' + tripId + '/settings'}><Button variant='outline'>Settings</Button></Link> : null}
              {trip?.is_owner ? <ShareTripButton tripId={tripId} /> : null}
              <SyncTripButton tripId={tripId} />
            </div>
          </CardContent>
        </Card>

        {trip ? <TripEventsPlanner categories={trip.event_categories} initialEvents={events} trip={trip} /> : null}
      </div>
    </AppShell>
  );
}
