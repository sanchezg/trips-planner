import Link from "next/link";
import { redirect } from "next/navigation";
import { AppShell } from "@/components/shared/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getGoogleLoginUrl } from "@/features/auth/api";
import { getCurrentUser } from "@/lib/auth/session";

const LOGIN_ERROR_MESSAGES: Record<string, string> = {
  unauthorized_email: "This Google account is not allowed to access the app. Contact an administrator if you need access."
};

export default async function LoginPage({
  searchParams,
}: {
  searchParams?: Promise<{ error?: string }>;
}) {
  const user = await getCurrentUser();

  if (user) {
    redirect("/dashboard");
  }

  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const errorMessage = resolvedSearchParams?.error ? LOGIN_ERROR_MESSAGES[resolvedSearchParams.error] : undefined;
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
          {errorMessage ? (
            <div className="rounded-2xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {errorMessage}
            </div>
          ) : null}
          <div className="flex flex-wrap gap-3">
            <Link href={googleLoginUrl}><Button>Sign in with Google</Button></Link>
            <Link href={googleLoginUrl}><Button variant="outline">Log in with Google</Button></Link>
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
