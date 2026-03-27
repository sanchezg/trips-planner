import { apiFetch } from "@/lib/api-client";

export async function getIntegrationHealth() {
  return apiFetch<{ auth: string; calendar: string; maps: string }>("/api/routes/integrations/status");
}
