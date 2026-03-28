import { z } from "zod";

export const tripCreateSchema = z.object({
  name: z.string().min(3),
  description: z.string().max(500).optional(),
  startsAt: z.string().optional(),
  endsAt: z.string().optional(),
  flightNumber: z.string().max(20).optional(),
  airport: z.string().max(120).optional(),
  visibility: z.enum(["private", "shared"]).default("private")
}).refine((value) => {
  if (!value.startsAt || !value.endsAt) {
    return true;
  }
  return new Date(value.startsAt).getTime() <= new Date(value.endsAt).getTime();
}, {
  message: "Departure must be after arrival.",
  path: ["endsAt"]
});

export type TripCreateInput = z.infer<typeof tripCreateSchema>;
