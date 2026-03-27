const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function getGoogleLoginUrl() {
  return API_BASE_URL + "/api/routes/auth/google/login";
}
