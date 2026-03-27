import { z } from "zod";

export const tripCreateSchema = z.object({
  name: z.string().min(3),
  description: z.string().max(500).optional(),
  startsAt: z.string().optional(),
  endsAt: z.string().optional(),
  visibility: z.enum(["private", "shared"]).default("private")
});

export type TripCreateInput = z.infer<typeof tripCreateSchema>;
