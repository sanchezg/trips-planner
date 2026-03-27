'use client';

import { useState, useTransition } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { updateTripSettings, type TripSettings } from '@/features/trips/api';
import { tripSettingsSchema, type TripSettingsFormValues, type TripSettingsInput } from '@/lib/validations/trip-settings';

export function TripSettingsForm({ initialSettings, tripId }: { initialSettings: TripSettings; tripId: string }) {
  const [isPending, startTransition] = useTransition();
  const [message, setMessage] = useState<string | null>(null);
  const router = useRouter();
  const form = useForm<TripSettingsFormValues, unknown, TripSettingsInput>({
    defaultValues: {
      categoriesInput: initialSettings.event_categories.join(', '),
      calendarAutoSync: initialSettings.calendar_auto_sync
    },
    resolver: zodResolver(tripSettingsSchema)
  });

  return (
    <Card>
      <CardHeader>
        <Badge>Trip settings</Badge>
        <CardTitle className='mt-2'>Events and calendar sync</CardTitle>
      </CardHeader>
      <CardContent>
        <form className='space-y-5' onSubmit={form.handleSubmit((values) => {
          startTransition(async () => {
            try {
              const settings = await updateTripSettings(tripId, values);
              setMessage('Settings saved.');
              form.reset({
                categoriesInput: settings.event_categories.join(', '),
                calendarAutoSync: settings.calendar_auto_sync
              });
              router.refresh();
            } catch (error) {
              setMessage(error instanceof Error ? error.message : 'Unable to save settings.');
            }
          });
        })}>
          <label className='space-y-2 text-sm'>
            <span>Event categories</span>
            <textarea className='min-h-28 w-full rounded-[1.35rem] border border-border bg-input px-4 py-3 text-sm placeholder:text-muted-foreground focus:border-primary focus:outline-none' {...form.register('categoriesInput')} placeholder='transit, travel, stay, entertainment, meal' />
            <p className='text-xs text-muted-foreground'>Separate categories with commas. These options will be suggested when creating or editing events for this trip.</p>
          </label>

          <label className='flex items-start gap-3 rounded-[1.35rem] border border-border bg-muted/30 px-4 py-4 text-sm'>
            <input className='mt-1 h-4 w-4 rounded border-border' type='checkbox' {...form.register('calendarAutoSync')} />
            <span>
              <span className='block font-medium'>Auto sync with Google Calendar</span>
              <span className='mt-1 block text-muted-foreground'>When enabled, this trip is marked for automatic calendar sync once the calendar integration is connected.</span>
            </span>
          </label>

          {message ? <p className='text-sm text-muted-foreground'>{message}</p> : null}

          <div className='flex flex-wrap gap-3'>
            <Button disabled={isPending} type='submit'>{isPending ? 'Saving...' : 'Save settings'}</Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
