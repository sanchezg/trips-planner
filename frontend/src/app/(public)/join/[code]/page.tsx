import { AppShell } from '@/components/shared/app-shell';
import { JoinTripLink } from '@/components/trips/join-trip-link';
import { getCurrentUser } from '@/lib/auth/session';
import { extractTripShareCode } from '@/features/trips/api';

export default async function JoinTripByUrlPage({ params }: { params: Promise<{ code: string }> }) {
  const [{ code }, user] = await Promise.all([params, getCurrentUser()]);
  const resolvedCode = extractTripShareCode(code);

  return (
    <AppShell
      eyebrow='Shared trip'
      title='Join a shared trip'
      description='Open a shared trip invite, sign in if needed, and add it to your trips workspace.'
    >
      <JoinTripLink code={resolvedCode} isAuthenticated={Boolean(user)} />
    </AppShell>
  );
}
