const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function getGoogleLoginUrl(nextPath?: string) {
  if (!nextPath) {
    return API_BASE_URL + "/api/routes/auth/google/login";
  }

  const query = new URLSearchParams({ next: nextPath });
  return API_BASE_URL + "/api/routes/auth/google/login?" + query.toString();
}
