import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function TripExpensesPage({ params }: { params: Promise<{ tripId: string }> }) {
  const { tripId } = await params;
  return (
    <AppShell eyebrow="Expenses" title="Trip expenses" description={"Expense summaries, categorization, and event or destination associations live in the backend expenses module for trip " + tripId + "."}>
      <Card>
        <CardHeader><CardTitle>Expenses module shell</CardTitle></CardHeader>
        <CardContent><p className="text-sm leading-6 text-muted-foreground">Add expense forms and reports here as the backend expense endpoints mature.</p></CardContent>
      </Card>
    </AppShell>
  );
}
