'use client';

import { useState, useTransition } from 'react';
import { Button } from '@/components/ui/button';
import { createTripShareCode, type ShareableTripRole } from '@/features/trips/api';

export function ShareTripButton({ tripId }: { tripId: string }) {
  const [isPending, startTransition] = useTransition();
  const [shareCodes, setShareCodes] = useState<Partial<Record<ShareableTripRole, string>>>({});
  const [message, setMessage] = useState<string | null>(null);

  function handleGenerate(role: ShareableTripRole) {
    startTransition(async () => {
      try {
        const response = await createTripShareCode(tripId, role);
        setShareCodes((current) => ({
          ...current,
          [response.role]: response.share_code,
        }));
        setMessage(`Share the ${response.role} code with the person you want to invite.`);
      } catch (error) {
        setMessage(error instanceof Error ? error.message : 'Unable to generate a share code.');
      }
    });
  }

  return (
    <div className='space-y-2'>
      <div className='flex flex-wrap gap-2'>
        <Button disabled={isPending} onClick={() => handleGenerate('editor')} type='button' variant='outline'>
          {isPending ? 'Generating...' : 'Share as editor'}
        </Button>
        <Button disabled={isPending} onClick={() => handleGenerate('viewer')} type='button' variant='outline'>
          {isPending ? 'Generating...' : 'Share as viewer'}
        </Button>
      </div>
      {shareCodes.editor ? <p className='text-xs font-semibold uppercase tracking-[0.18em] text-primary'>Editor code: {shareCodes.editor}</p> : null}
      {shareCodes.viewer ? <p className='text-xs font-semibold uppercase tracking-[0.18em] text-primary'>Viewer code: {shareCodes.viewer}</p> : null}
      {message ? <p className='text-xs text-muted-foreground'>{message}</p> : null}
    </div>
  );
}
