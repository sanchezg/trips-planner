'use client';

import Link from 'next/link';
import { useEffect, useRef, useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getGoogleLoginUrl } from '@/features/auth/api';
import { joinTrip } from '@/features/trips/api';

export function JoinTripLink({ code, isAuthenticated }: { code: string; isAuthenticated: boolean }) {
  const [message, setMessage] = useState<string>('Preparing trip access...');
  const [isPending, startTransition] = useTransition();
  const hasAttemptedJoinRef = useRef(false);
  const router = useRouter();
  const loginUrl = getGoogleLoginUrl('/join/' + code);

  useEffect(() => {
    if (isAuthenticated === false || hasAttemptedJoinRef.current) {
      return;
    }

    hasAttemptedJoinRef.current = true;
    startTransition(async () => {
      try {
        const trip = await joinTrip(code);
        setMessage('Trip joined with ' + trip.membership_role + ' access. Redirecting...');
        router.replace('/trips/' + trip.id);
      } catch (error) {
        setMessage(error instanceof Error ? error.message : 'Unable to join this shared trip.');
      }
    });
  }, [code, isAuthenticated, router]);

  if (isAuthenticated === false) {
    return (
      <Card className='max-w-2xl'>
        <CardHeader>
          <CardTitle>Join a shared trip</CardTitle>
        </CardHeader>
        <CardContent className='space-y-4'>
          <p className='text-sm leading-6 text-muted-foreground'>
            Sign in with Google to accept this trip invite and add it to your workspace.
          </p>
          <Link href={loginUrl}><Button>Sign in to join</Button></Link>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className='max-w-2xl'>
      <CardHeader>
        <CardTitle>Joining shared trip</CardTitle>
      </CardHeader>
      <CardContent className='space-y-4'>
        <p className='text-sm leading-6 text-muted-foreground'>{message}</p>
        {(message === 'Preparing trip access...' || isPending) ? <p className='text-xs text-muted-foreground'>Hold on while we connect this trip to your account.</p> : null}
      </CardContent>
    </Card>
  );
}
