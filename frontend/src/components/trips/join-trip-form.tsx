'use client';

import { useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { extractTripShareCode, joinTrip } from '@/features/trips/api';

export function JoinTripForm() {
  const [codeOrUrl, setCodeOrUrl] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const router = useRouter();
  const resolvedCode = extractTripShareCode(codeOrUrl);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Join a trip</CardTitle>
      </CardHeader>
      <CardContent>
        <form className='space-y-4' onSubmit={(event) => {
          event.preventDefault();
          startTransition(async () => {
            try {
              const trip = await joinTrip(codeOrUrl);
              setMessage(`Trip joined with ${trip.membership_role} access.`);
              router.push('/trips/' + trip.id);
            } catch (error) {
              setMessage(error instanceof Error ? error.message : 'Unable to join trip.');
            }
          });
        }}>
          <label className='space-y-2 text-sm'>
            <span>Shared code or URL</span>
            <Input onChange={(event) => setCodeOrUrl(event.target.value)} placeholder='AB12CD34 or https://app.example.com/join/AB12CD34' value={codeOrUrl} />
          </label>
          <Button disabled={isPending || !resolvedCode} type='submit'>
            {isPending ? 'Joining...' : 'Join trip'}
          </Button>
          {message ? <p className='text-sm text-muted-foreground'>{message}</p> : null}
        </form>
      </CardContent>
    </Card>
  );
}
