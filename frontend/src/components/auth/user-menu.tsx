"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import type { AuthUser } from "@/lib/auth/session";

export function UserMenu({ user }: { user: AuthUser }) {
  const [isPending, setIsPending] = useState(false);
  const router = useRouter();

  async function handleLogout() {
    setIsPending(true);
    try {
      await fetch((process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000") + "/api/routes/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } finally {
      router.push("/login");
      router.refresh();
      setIsPending(false);
    }
  }

  return (
    <div className="flex items-center gap-3 rounded-full border border-border bg-white px-3 py-2 shadow-sm">
      <div className="min-w-0 text-right">
        <p className="truncate text-sm font-medium text-foreground">{user.name ?? "Signed in"}</p>
        <p className="truncate text-xs text-muted-foreground">{user.email}</p>
      </div>
      <Button onClick={handleLogout} disabled={isPending} variant="outline" type="button">
        {isPending ? "Signing out..." : "Log out"}
      </Button>
    </div>
  );
}
