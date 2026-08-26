"use client";

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { homeRouteForRole, loginResponseToToken } from "@/lib/api";
import { useAuth } from "@/providers/auth-provider";
import { useNotice } from "@/providers/notice-provider";
import type { Role } from "@/types/recruitment";

function OAuthCallbackContent() {
  const router = useRouter();
  const params = useSearchParams();
  const { login } = useAuth();
  const { showNotice } = useNotice();

  useEffect(() => {
    const requires2fa = params.get("requires_2fa");
    const loginChallenge = params.get("login_challenge");
    const role = (params.get("role") as Role) || "student";
    const accessToken = params.get("access_token");
    const refreshToken = params.get("refresh_token");

    if (requires2fa === "1" && loginChallenge) {
      router.replace(`/login?requires_2fa=1&login_challenge=${encodeURIComponent(loginChallenge)}&role=${role}`);
      return;
    }

    if (accessToken) {
      login(
        loginResponseToToken(
          {
            access_token: accessToken,
            refresh_token: refreshToken,
            role,
          },
          role,
        ),
      );
      showNotice("Signed in with OAuth.");
      router.replace(homeRouteForRole(role));
      return;
    }

    showNotice("OAuth sign-in failed.");
    router.replace("/login");
  }, [login, params, router, showNotice]);

  return <main className="page-shell">Completing OAuth sign-in...</main>;
}

export default function OAuthCallbackPage() {
  return (
    <Suspense fallback={<main className="page-shell">Completing OAuth sign-in...</main>}>
      <OAuthCallbackContent />
    </Suspense>
  );
}
