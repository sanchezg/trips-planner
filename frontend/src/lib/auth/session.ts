import { cookies } from "next/headers";

export type AuthUser = {
  id: string;
  email: string;
  name?: string | null;
};

function getApiBaseUrl() {
  return process.env.API_BASE_URL_INTERNAL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}

export async function getCurrentUser(): Promise<AuthUser | null> {
  const cookieStore = await cookies();
  const response = await fetch(getApiBaseUrl() + "/api/routes/auth/me", {
    headers: {
      cookie: cookieStore.toString(),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    return null;
  }

  return response.json() as Promise<AuthUser>;
}
