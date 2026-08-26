"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { homeRouteForRole } from "@/lib/api";
import { useAuth } from "@/providers/auth-provider";
import type { Role } from "@/types/recruitment";

export function RequireAuth({ role, children }: { role?: Role; children: React.ReactNode }) {
  const router = useRouter();
  const { token, ready } = useAuth();

  useEffect(() => {
    if (!ready) return;
    if (!token) {
      router.replace("/login");
      return;
    }
    if (role && token.role !== role) {
      router.replace(homeRouteForRole(token.role));
    }
  }, [ready, token, role, router]);

  if (!ready || !token || (role && token.role !== role)) {
    return null;
  }

  return <>{children}</>;
}
