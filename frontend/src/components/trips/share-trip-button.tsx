'use client';

import { useState, useTransition } from 'react';
import { Button } from '@/components/ui/button';
import { createTripShareCode } from '@/features/trips/api';

export function ShareTripButton({ tripId }: { tripId: string }) {
  const [isPending, startTransition] = useTransition();
  const [shareCode, setShareCode] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  return (
    <div className='space-y-2'>
      <Button onClick={() => {
        startTransition(async () => {
          try {
            const response = await createTripShareCode(tripId);
            setShareCode(response.share_code);
            setMessage('Share this code with the person you want to invite.');
          } catch (error) {
            setMessage(error instanceof Error ? error.message : 'Unable to generate a share code.');
          }
        });
      }} type='button' variant='outline'>
        {isPending ? 'Generating...' : 'Share trip'}
      </Button>
      {shareCode ? <p className='text-xs font-semibold uppercase tracking-[0.18em] text-primary'>Code: {shareCode}</p> : null}
      {message ? <p className='text-xs text-muted-foreground'>{message}</p> : null}
    </div>
  );
}
