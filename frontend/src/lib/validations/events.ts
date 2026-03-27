import { z } from 'zod';

const optionalText = (max: number) => z.string().trim().max(max).transform((value) => value || undefined);

export const eventFormSchema = z
  .object({
    destinationId: optionalText(120),
    title: z.string().trim().min(1, 'Event title is required.').max(120),
    category: optionalText(80),
    address: optionalText(160),
    startsAt: z.string().min(1, 'Start date and time are required.'),
    endsAt: z.string().min(1, 'End date and time are required.'),
    notes: optionalText(2000)
  })
  .superRefine(({ startsAt, endsAt }, ctx) => {
    const startsAtDate = new Date(startsAt);
    const endsAtDate = new Date(endsAt);

    if (Number.isNaN(startsAtDate.getTime()) || Number.isNaN(endsAtDate.getTime())) {
      ctx.addIssue({
        code: 'custom',
        path: ['startsAt'],
        message: 'Use valid dates for the event.'
      });
      return;
    }

    if (endsAtDate <= startsAtDate) {
      ctx.addIssue({
        code: 'custom',
        path: ['endsAt'],
        message: 'End date and time must be after the start.'
      });
    }
  });

export type EventFormValues = z.input<typeof eventFormSchema>;
export type EventFormInput = z.output<typeof eventFormSchema>;
