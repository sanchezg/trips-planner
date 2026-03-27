import { TripSettingsForm } from '@/components/trips/trip-settings-form';
import { AppShell } from '@/components/shared/app-shell';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getTripSettings } from '@/features/trips/api';

export default async function TripSettingsPage({ params }: { params: Promise<{ tripId: string }> }) {
  const { tripId } = await params;
  const settings = await getTripSettings(tripId).catch(() => null);

  return (
    <AppShell eyebrow='Settings' title='Trip settings' description={'Configure event categories and calendar sync preferences for trip ' + tripId + '.'}>
      <div className='space-y-6'>
        {settings ? <TripSettingsForm initialSettings={settings} tripId={tripId} /> : null}
        <Card>
          <CardHeader><CardTitle>What these settings control</CardTitle></CardHeader>
          <CardContent><p className='text-sm leading-6 text-muted-foreground'>Custom categories appear in the trip event planner, and calendar auto sync marks whether this trip should push future changes to Google Calendar automatically.</p></CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
