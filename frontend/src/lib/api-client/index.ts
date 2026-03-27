function getApiBaseUrl() {
  if (typeof window === "undefined") {
    return process.env.API_BASE_URL_INTERNAL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
  }

  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers ?? {});

  if (!headers.has("Content-Type") && init?.body) {
    headers.set("Content-Type", "application/json");
  }

  if (typeof window === "undefined") {
    const { cookies } = await import("next/headers");
    const cookieStore = await cookies();
    const cookieHeader = cookieStore.toString();

    if (cookieHeader) {
      headers.set("cookie", cookieHeader);
    }
  }

  const response = await fetch(getApiBaseUrl() + path, {
    ...init,
    credentials: "include",
    headers,
    cache: "no-store"
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `API request failed for ${path}`);
  }

  return response.json() as Promise<T>;
}
