import Link from "next/link";
import { redirect } from "next/navigation";
import { AppShell } from "@/components/shared/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getGoogleLoginUrl } from "@/features/auth/api";
import { getCurrentUser } from "@/lib/auth/session";

export default async function LoginPage() {
  const user = await getCurrentUser();

  if (user) {
    redirect("/dashboard");
  }

  return (
    <AppShell eyebrow="Public" title="Trips Planner" description="Your personal travel assistant. Plan your trips, explore new destinations, and manage your travel itineraries with ease.">
      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Sign-in with Google</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm leading-6 text-muted-foreground">
            Sign-in here and start flying ✈️
          </p>
          <div className="flex flex-wrap gap-3">
            <Link href={getGoogleLoginUrl()}><Button>Continue with Google</Button></Link>
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
