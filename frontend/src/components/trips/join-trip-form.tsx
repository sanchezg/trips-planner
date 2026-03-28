'use client';

import { useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { joinTrip } from '@/features/trips/api';

export function JoinTripForm() {
  const [code, setCode] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const router = useRouter();

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
              const trip = await joinTrip(code);
              setMessage(`Trip joined with ${trip.membership_role} access.`);
              router.push('/trips/' + trip.id);
            } catch (error) {
              setMessage(error instanceof Error ? error.message : 'Unable to join trip.');
            }
          });
        }}>
          <label className='space-y-2 text-sm'>
            <span>Shared code</span>
            <Input onChange={(event) => setCode(event.target.value.toUpperCase())} placeholder='AB12CD34' value={code} />
          </label>
          <Button disabled={isPending || !code.trim()} type='submit'>
            {isPending ? 'Joining...' : 'Join trip'}
          </Button>
          {message ? <p className='text-sm text-muted-foreground'>{message}</p> : null}
        </form>
      </CardContent>
    </Card>
  );
}
