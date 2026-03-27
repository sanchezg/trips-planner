import { z } from 'zod';

export const tripSettingsSchema = z.object({
  categoriesInput: z.string().min(1, 'Add at least one category.'),
  calendarAutoSync: z.boolean()
}).transform(({ categoriesInput, calendarAutoSync }) => {
  const eventCategories = categoriesInput
    .split(',')
    .map((value) => value.trim().toLowerCase())
    .filter(Boolean)
    .filter((value, index, values) => values.indexOf(value) === index);

  if (!eventCategories.length) {
    throw new Error('Add at least one category.');
  }

  return {
    eventCategories,
    calendarAutoSync
  };
});

export type TripSettingsFormValues = z.input<typeof tripSettingsSchema>;
export type TripSettingsInput = z.output<typeof tripSettingsSchema>;
