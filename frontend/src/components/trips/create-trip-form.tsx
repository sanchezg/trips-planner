"use client";

import { useState, useTransition } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { createTrip } from "@/features/trips/api";
import { tripCreateSchema } from "@/lib/validations/trips";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

type TripCreateInput = z.input<typeof tripCreateSchema>;
type TripCreateOutput = z.output<typeof tripCreateSchema>;

export function CreateTripForm() {
  const [isPending, startTransition] = useTransition();
  const [message, setMessage] = useState<string | null>(null);
  const router = useRouter();
  const form = useForm<TripCreateInput, unknown, TripCreateOutput>({
    defaultValues: {
      name: "",
      description: "",
      startsAt: "",
      endsAt: "",
      visibility: "private"
    },
    resolver: zodResolver(tripCreateSchema)
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Create a trip</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={form.handleSubmit((values) => {
          startTransition(async () => {
            try {
              const trip = await createTrip(values);
              setMessage("Trip created successfully.");
              router.push("/trips/" + trip.id);
            } catch (error) {
              setMessage(error instanceof Error ? error.message : "Unable to create trip.");
            }
          });
        })}>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2 text-sm">
              <span>Trip name</span>
              <Input {...form.register("name")} placeholder="Autumn in Lisbon" />
            </label>
            <label className="space-y-2 text-sm">
              <span>Visibility</span>
              <select className="h-11 w-full rounded-2xl border border-border bg-white px-4 text-sm" {...form.register("visibility")}>
                <option value="private">Private</option>
                <option value="shared">Shared</option>
              </select>
            </label>
          </div>

          <label className="space-y-2 text-sm">
            <span>Description</span>
            <textarea className="min-h-28 w-full rounded-2xl border border-border bg-white px-4 py-3 text-sm" {...form.register("description")} placeholder="What kind of trip is this?" />
          </label>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2 text-sm">
              <span>Starts at</span>
              <Input type="date" {...form.register("startsAt")} />
            </label>
            <label className="space-y-2 text-sm">
              <span>Ends at</span>
              <Input type="date" {...form.register("endsAt")} />
            </label>
          </div>

          <Button disabled={isPending} type="submit">
            {isPending ? "Creating..." : "Create trip"}
          </Button>
          {message ? <p className="text-sm text-muted-foreground">{message}</p> : null}
        </form>
      </CardContent>
    </Card>
  );
}
