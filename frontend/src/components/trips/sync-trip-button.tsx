'use client';

import { useState, useTransition } from 'react';
import { Button } from '@/components/ui/button';
import { syncTripToGoogleCalendar } from '@/features/calendar/api';

export function SyncTripButton({ tripId }: { tripId: string }) {
  const [message, setMessage] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  return (
    <div className='space-y-2'>
      <Button onClick={() => {
        startTransition(async () => {
          try {
            const response = await syncTripToGoogleCalendar(tripId);
            setMessage(response.message);
          } catch (error) {
            setMessage(error instanceof Error ? error.message : 'Unable to sync trip to Google Calendar.');
          }
        });
      }} type='button' variant='outline'>
        {isPending ? 'Syncing...' : 'Sync to Google Calendar'}
      </Button>
      {message ? <p className='text-xs text-muted-foreground'>{message}</p> : null}
    </div>
  );
}
