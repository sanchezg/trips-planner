'use client';

import { useState, useTransition } from 'react';
import { Button } from '@/components/ui/button';
import { createTripShareCode, type ShareableTripRole } from '@/features/trips/api';

type ShareLinkMap = Partial<Record<ShareableTripRole, { code: string; url: string }>>;

function buildShareUrl(code: string) {
  if (typeof window === 'undefined') {
    return `/join/${code}`;
  }
  return `${window.location.origin}/join/${code}`;
}

export function ShareTripButton({ tripId }: { tripId: string }) {
  const [isPending, startTransition] = useTransition();
  const [shareLinks, setShareLinks] = useState<ShareLinkMap>({});
  const [message, setMessage] = useState<string | null>(null);

  function handleGenerate(role: ShareableTripRole) {
    startTransition(async () => {
      try {
        const response = await createTripShareCode(tripId, role);
        const shareUrl = buildShareUrl(response.share_code);
        setShareLinks((current) => ({
          ...current,
          [response.role]: {
            code: response.share_code,
            url: shareUrl,
          },
        }));
        setMessage(`Share the ${response.role} link or code with the person you want to invite.`);
      } catch (error) {
        setMessage(error instanceof Error ? error.message : 'Unable to generate a share link.');
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
      {shareLinks.editor ? (
        <div className='space-y-1 text-xs text-muted-foreground'>
          <p className='font-semibold uppercase tracking-[0.18em] text-primary'>Editor code: {shareLinks.editor.code}</p>
          <p className='break-all'>Editor link: {shareLinks.editor.url}</p>
        </div>
      ) : null}
      {shareLinks.viewer ? (
        <div className='space-y-1 text-xs text-muted-foreground'>
          <p className='font-semibold uppercase tracking-[0.18em] text-primary'>Viewer code: {shareLinks.viewer.code}</p>
          <p className='break-all'>Viewer link: {shareLinks.viewer.url}</p>
        </div>
      ) : null}
      {message ? <p className='text-xs text-muted-foreground'>{message}</p> : null}
    </div>
  );
}
