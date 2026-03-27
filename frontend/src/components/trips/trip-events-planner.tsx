'use client';

import { useEffect, useMemo, useState, useTransition } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { CalendarDays, Clock3, MapPin, Pencil, Plus, Trash2 } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { createTripEvent, deleteTripEvent, type TripEvent, updateTripEvent } from '@/features/events/api';
import type { TripSummary } from '@/features/trips/api';
import { eventFormSchema, type EventFormInput, type EventFormValues } from '@/lib/validations/events';
import { cn } from '@/lib/utils';

const dayNumberFormatter = new Intl.DateTimeFormat('en', { day: 'numeric' });
const dayLabelFormatter = new Intl.DateTimeFormat('en', { weekday: 'short' });
const eventDateFormatter = new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
const sectionDateFormatter = new Intl.DateTimeFormat('en', { month: 'long', day: 'numeric', year: 'numeric' });

type TripEventsPlannerProps = {
  categories: string[];
  trip: TripSummary;
  initialEvents: TripEvent[];
};

type TripDay = {
  iso: string;
  label: string;
  weekday: string;
  eventCount: number;
};

function sortEvents(events: TripEvent[]) {
  return [...events].sort((left, right) => new Date(left.starts_at).getTime() - new Date(right.starts_at).getTime());
}

function toDateKey(value: string) {
  return new Date(value).toISOString().slice(0, 10);
}

function formatDayKey(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function toCalendarDate(value: string) {
  const date = new Date(value);
  return new Date(date.getFullYear(), date.getMonth(), date.getDate(), 12);
}

function getCoveredDayKeys(event: TripEvent) {
  const cursor = toCalendarDate(event.starts_at);
  const end = toCalendarDate(event.ends_at);
  const coveredDays = new Set<string>();

  while (cursor <= end) {
    coveredDays.add(formatDayKey(cursor));
    cursor.setDate(cursor.getDate() + 1);
  }

  return coveredDays;
}

function isEventOnDay(event: TripEvent, dayKey: string) {
  return getCoveredDayKeys(event).has(dayKey);
}

function getEventsForDay(events: TripEvent[], dayKey: string | null) {
  if (!dayKey) {
    return [];
  }

  return sortEvents(events).filter((event) => isEventOnDay(event, dayKey));
}

function getInitialSelectedDay(trip: TripSummary, events: TripEvent[], tripDays: TripDay[]) {
  const firstEvent = sortEvents(events)[0];
  if (firstEvent) {
    return toDateKey(firstEvent.starts_at);
  }

  return trip.starts_at ?? tripDays[0]?.iso ?? null;
}

function toDateTimeLocalValue(value: string) {
  const date = new Date(value);
  const offset = date.getTimezoneOffset();
  const localDate = new Date(date.getTime() - offset * 60_000);
  return localDate.toISOString().slice(0, 16);
}

function buildDefaultDateTime(dateValue: string | null, hour: number) {
  const date = dateValue ?? new Date().toISOString().slice(0, 10);
  return `${date}T${String(hour).padStart(2, '0')}:00`;
}

function toFormDefaults(trip: TripSummary, event?: TripEvent | null): EventFormValues {
  if (event) {
    return {
      destinationId: event.destination_id ?? '',
      title: event.title,
      category: event.category ?? '',
      address: event.address ?? '',
      startsAt: toDateTimeLocalValue(event.starts_at),
      endsAt: toDateTimeLocalValue(event.ends_at),
      notes: event.notes ?? ''
    };
  }

  return {
    destinationId: '',
    title: '',
    category: trip.event_categories[0] ?? '',
    address: '',
    startsAt: buildDefaultDateTime(trip.starts_at, 9),
    endsAt: buildDefaultDateTime(trip.starts_at ?? trip.ends_at, 10),
    notes: ''
  };
}

function buildTripDays(trip: TripSummary, events: TripEvent[]): TripDay[] {
  if (!trip.starts_at || !trip.ends_at) {
    return [];
  }

  const eventCoverage = new Map<string, number>();
  for (const event of events) {
    for (const dayKey of getCoveredDayKeys(event)) {
      eventCoverage.set(dayKey, (eventCoverage.get(dayKey) ?? 0) + 1);
    }
  }

  const cursor = new Date(`${trip.starts_at}T12:00:00`);
  const end = new Date(`${trip.ends_at}T12:00:00`);
  const days: TripDay[] = [];

  while (cursor <= end && days.length < 62) {
    const iso = formatDayKey(cursor);
    days.push({
      iso,
      label: dayNumberFormatter.format(cursor),
      weekday: dayLabelFormatter.format(cursor),
      eventCount: eventCoverage.get(iso) ?? 0
    });
    cursor.setDate(cursor.getDate() + 1);
  }

  return days;
}

function groupEventsByDay(events: TripEvent[]) {
  const grouped = new Map<string, TripEvent[]>();

  for (const event of sortEvents(events)) {
    const dateKey = toDateKey(event.starts_at);
    const items = grouped.get(dateKey) ?? [];
    items.push(event);
    grouped.set(dateKey, items);
  }

  return Array.from(grouped.entries());
}

export function TripEventsPlanner({ categories, trip, initialEvents }: TripEventsPlannerProps) {
  const [events, setEvents] = useState(() => sortEvents(initialEvents));
  const [editingEventId, setEditingEventId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [isPending, startTransition] = useTransition();
  const editingEvent = events.find((event) => event.id === editingEventId) ?? null;
  const tripDays = useMemo(() => buildTripDays(trip, events), [trip, events]);
  const [selectedDay, setSelectedDay] = useState<string | null>(() => getInitialSelectedDay(trip, initialEvents, buildTripDays(trip, initialEvents)));
  const resolvedSelectedDay = useMemo(() => {
    if (!tripDays.length) {
      return null;
    }

    if (selectedDay && tripDays.some((day) => day.iso === selectedDay)) {
      return selectedDay;
    }

    return getInitialSelectedDay(trip, events, tripDays);
  }, [events, selectedDay, trip, tripDays]);
  const selectedDayEvents = useMemo(() => getEventsForDay(events, resolvedSelectedDay), [events, resolvedSelectedDay]);
  const groupedEvents = useMemo(() => groupEventsByDay(events), [events]);
  const form = useForm<EventFormValues, unknown, EventFormInput>({
    defaultValues: toFormDefaults(trip),
    resolver: zodResolver(eventFormSchema)
  });

  useEffect(() => {
    form.reset(toFormDefaults(trip, editingEvent));
  }, [editingEvent, form, trip]);

  function upsertEvent(nextEvent: TripEvent) {
    setEvents((currentEvents) => sortEvents(currentEvents.some((event) => event.id === nextEvent.id)
      ? currentEvents.map((event) => event.id === nextEvent.id ? nextEvent : event)
      : [...currentEvents, nextEvent]));
  }

  function handleCancelEdit() {
    setEditingEventId(null);
    setWarnings([]);
    setMessage(null);
    form.reset(toFormDefaults(trip));
  }

  function handleDelete(eventId: string) {
    if (!window.confirm('Remove this event from the trip?')) {
      return;
    }

    startTransition(async () => {
      try {
        await deleteTripEvent(eventId);
        setEvents((currentEvents) => currentEvents.filter((event) => event.id !== eventId));
        if (editingEventId === eventId) {
          handleCancelEdit();
        }
        setWarnings([]);
        setMessage('Event removed.');
      } catch (error) {
        setMessage(error instanceof Error ? error.message : 'Unable to remove the event.');
      }
    });
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
      <div className="space-y-6">
        <Card>
          <CardHeader className="flex flex-row items-start justify-between gap-4">
            <div className="space-y-2">
              <Badge>Trip calendar</Badge>
              <CardTitle className="flex items-center gap-2 text-xl">
                <CalendarDays className="h-5 w-5" />
                {trip.starts_at && trip.ends_at ? `${sectionDateFormatter.format(new Date(`${trip.starts_at}T12:00:00`))} to ${sectionDateFormatter.format(new Date(`${trip.ends_at}T12:00:00`))}` : 'Add trip dates to unlock the calendar overview'}
              </CardTitle>
            </div>
            <Badge className="bg-muted text-foreground">{events.length} event{events.length === 1 ? '' : 's'}</Badge>
          </CardHeader>
          <CardContent className="space-y-5">
            {tripDays.length ? (
              <>
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-7">
                  {tripDays.map((day) => {
                    const isSelected = resolvedSelectedDay === day.iso;
                    return (
                      <button
                        className={cn(
                          'rounded-3xl border px-4 py-3 text-left transition hover:border-primary hover:bg-accent/60',
                          isSelected ? 'border-primary bg-primary text-primary-foreground' : day.eventCount ? 'border-border bg-accent/60' : 'border-border bg-white'
                        )}
                        key={day.iso}
                        onClick={() => setSelectedDay(day.iso)}
                        type="button"
                      >
                        <p className={cn('text-xs font-semibold uppercase tracking-[0.18em]', isSelected ? 'text-primary-foreground/80' : 'text-muted-foreground')}>{day.weekday}</p>
                        <p className="mt-2 text-2xl font-semibold">{day.label}</p>
                        <p className={cn('mt-3 text-sm', isSelected ? 'text-primary-foreground/80' : 'text-muted-foreground')}>
                          {day.eventCount ? `${day.eventCount} planned` : 'Open day'}
                        </p>
                      </button>
                    );
                  })}
                </div>

                <div className="rounded-3xl border border-border bg-muted/30 px-5 py-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">Selected day</p>
                      <p className="mt-1 text-base font-semibold">
                        {resolvedSelectedDay ? sectionDateFormatter.format(new Date(`${resolvedSelectedDay}T12:00:00`)) : 'Pick a day'}
                      </p>
                    </div>
                    <Badge className="bg-white text-foreground">
                      {selectedDayEvents.length} event{selectedDayEvents.length === 1 ? '' : 's'}
                    </Badge>
                  </div>

                  {selectedDayEvents.length ? (
                    <div className="mt-4 space-y-3">
                      {selectedDayEvents.map((event) => (
                        <div className="rounded-3xl border border-border bg-white px-4 py-3" key={event.id}>
                          <div className="flex flex-wrap items-center justify-between gap-3">
                            <div>
                              <div className="flex flex-wrap items-center gap-2">
                                <p className="text-sm font-semibold">{event.title}</p>
                                {event.category ? <Badge>{event.category}</Badge> : null}
                              </div>
                              <p className="mt-2 text-sm text-muted-foreground">
                                {eventDateFormatter.format(new Date(event.starts_at))} to {eventDateFormatter.format(new Date(event.ends_at))}
                              </p>
                              {event.address ? <p className="mt-1 text-sm text-muted-foreground">{event.address}</p> : null}
                            </div>
                            <Button
                              onClick={() => {
                                setEditingEventId(event.id);
                                setWarnings([]);
                                setMessage(null);
                              }}
                              type="button"
                              variant="ghost"
                            >
                              <Pencil className="h-4 w-4" />
                              Edit
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="mt-4 text-sm text-muted-foreground">No events planned for this day yet.</p>
                  )}
                </div>
              </>
            ) : (
              <div className="rounded-3xl border border-dashed border-border px-5 py-6 text-sm text-muted-foreground">
                Set start and end dates on the trip to render a calendar for the travel window.
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between gap-4">
            <div>
              <Badge>Events</Badge>
              <CardTitle className="mt-2 text-xl">Itinerary by day</CardTitle>
            </div>
            <Button onClick={handleCancelEdit} type="button" variant="outline">
              <Plus className="h-4 w-4" />
              Add event
            </Button>
          </CardHeader>
          <CardContent className="space-y-5">
            {groupedEvents.length ? groupedEvents.map(([day, items]) => (
              <div className="space-y-3" key={day}>
                <div className="flex items-center justify-between border-b border-border pb-2">
                  <p className="text-sm font-semibold">{sectionDateFormatter.format(new Date(`${day}T12:00:00`))}</p>
                  <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{items.length} item{items.length === 1 ? '' : 's'}</p>
                </div>
                <div className="space-y-3">
                  {items.map((event) => (
                    <div className="rounded-3xl border border-border bg-white px-4 py-4" key={event.id}>
                      <div className="flex flex-wrap items-start justify-between gap-4">
                        <div className="space-y-2">
                          <div className="flex flex-wrap items-center gap-2">
                            <p className="text-base font-semibold">{event.title}</p>
                            {event.category ? <Badge>{event.category}</Badge> : null}
                          </div>
                          <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                            <span className="inline-flex items-center gap-2"><Clock3 className="h-4 w-4" />{eventDateFormatter.format(new Date(event.starts_at))} to {eventDateFormatter.format(new Date(event.ends_at))}</span>
                            {event.address ? <span className="inline-flex items-center gap-2"><MapPin className="h-4 w-4" />{event.address}</span> : null}
                          </div>
                          {event.notes ? <p className="text-sm leading-6 text-muted-foreground">{event.notes}</p> : null}
                        </div>
                        <div className="flex gap-2">
                          <Button onClick={() => {
                            setEditingEventId(event.id);
                            setWarnings([]);
                            setMessage(null);
                          }} type="button" variant="outline">
                            <Pencil className="h-4 w-4" />
                            Edit
                          </Button>
                          <Button onClick={() => handleDelete(event.id)} type="button" variant="ghost">
                            <Trash2 className="h-4 w-4" />
                            Remove
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )) : (
              <div className="rounded-3xl border border-dashed border-border px-5 py-6 text-sm text-muted-foreground">
                No events yet. Add the first stop, reservation, or activity for this trip.
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="h-fit xl:sticky xl:top-8">
        <CardHeader>
          <Badge>{editingEvent ? 'Edit event' : 'Create event'}</Badge>
          <CardTitle className="mt-2 text-xl">{editingEvent ? `Update ${editingEvent.title}` : 'Plan a new event'}</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={form.handleSubmit((values) => {
            startTransition(async () => {
              try {
                const response = editingEvent
                  ? await updateTripEvent(editingEvent.id, trip.id, values)
                  : await createTripEvent(trip.id, values);

                upsertEvent(response.event);
                setWarnings(response.warnings);
                setMessage(editingEvent ? 'Event updated.' : 'Event added to the trip.');
                setEditingEventId(null);
                form.reset(toFormDefaults(trip));
              } catch (error) {
                setMessage(error instanceof Error ? error.message : 'Unable to save the event.');
              }
            });
          })}>
            <label className="space-y-2 text-sm">
              <span>Title</span>
              <Input {...form.register('title')} placeholder="Dinner at the harbor" />
            </label>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="space-y-2 text-sm">
                <span>Category</span>
                <input className="flex h-11 w-full rounded-2xl border border-border bg-input px-4 py-2 text-sm placeholder:text-muted-foreground focus:border-primary focus:outline-none" list="trip-event-categories" {...form.register('category')} placeholder="Choose or type a category" />
                <datalist id="trip-event-categories">
                  {categories.map((category) => <option key={category} value={category} />)}
                </datalist>
              </label>
              <label className="space-y-2 text-sm">
                <span>Destination ID</span>
                <Input {...form.register('destinationId')} placeholder="Optional destination reference" />
              </label>
            </div>

            <label className="space-y-2 text-sm">
              <span>Address</span>
              <Input {...form.register('address')} placeholder="Street, venue, or meeting point" />
            </label>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="space-y-2 text-sm">
                <span>Starts at</span>
                <Input type="datetime-local" {...form.register('startsAt')} />
              </label>
              <label className="space-y-2 text-sm">
                <span>Ends at</span>
                <Input type="datetime-local" {...form.register('endsAt')} />
              </label>
            </div>

            <label className="space-y-2 text-sm">
              <span>Notes</span>
              <textarea className="min-h-32 w-full rounded-[1.35rem] border border-border bg-input px-4 py-3 text-sm placeholder:text-muted-foreground focus:border-primary focus:outline-none" {...form.register('notes')} placeholder="Add confirmations, companions, or reminders." />
            </label>

            {warnings.length ? (
              <div className="rounded-3xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
                <p className="font-semibold">Heads up</p>
                <ul className="mt-2 space-y-1">
                  {warnings.map((warning) => <li key={warning}>{warning}</li>)}
                </ul>
              </div>
            ) : null}

            {message ? <p className="text-sm text-muted-foreground">{message}</p> : null}

            <div className="flex flex-wrap gap-3">
              <Button disabled={isPending} type="submit">{isPending ? 'Saving...' : editingEvent ? 'Save changes' : 'Add event'}</Button>
              {editingEvent ? <Button onClick={handleCancelEdit} type="button" variant="outline">Cancel</Button> : null}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
