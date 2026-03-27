import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function TripSettingsPage({ params }: { params: Promise<{ tripId: string }> }) {
  const { tripId } = await params;
  return (
    <AppShell eyebrow="Settings" title="Trip settings" description={"Use this area for ownership, invitations, roles, and integration settings for trip " + tripId + "."}>
      <Card>
        <CardHeader><CardTitle>Collaboration settings shell</CardTitle></CardHeader>
        <CardContent><p className="text-sm leading-6 text-muted-foreground">Owners, editors, viewers, and invitation workflows are modeled by the backend and surfaced here via REST.</p></CardContent>
      </Card>
    </AppShell>
  );
}
