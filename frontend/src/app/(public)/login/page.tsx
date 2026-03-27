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

  const googleLoginUrl = getGoogleLoginUrl();

  return (
    <AppShell eyebrow="Public" title="Trips Planner" description="Your personal travel assistant. Plan your trips, explore new destinations, and manage your travel itineraries with ease.">
      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Sign in or log in with Google</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm leading-6 text-muted-foreground">
            Use either action below to enter your trips workspace with the same Google account flow.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link href={googleLoginUrl}><Button>Sign in with Google</Button></Link>
            <Link href={googleLoginUrl}><Button variant="outline">Log in with Google</Button></Link>
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
