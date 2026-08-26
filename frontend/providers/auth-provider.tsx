"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { clearToken, homeRouteForRole, loadToken, saveToken, setAuthHandlers } from "@/lib/api";
import type { Token } from "@/types/recruitment";

type AuthContextValue = {
  token: Token | null;
  ready: boolean;
  login: (token: Token, persist?: boolean) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [token, setToken] = useState<Token | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setToken(loadToken());
    setReady(true);
  }, []);

  useEffect(() => {
    setAuthHandlers({
      onTokenRefreshed: (next) => setToken(next),
      onAuthFailed: () => {
        clearToken();
        setToken(null);
        router.replace("/login");
      },
    });
    return () => setAuthHandlers({});
  }, [router]);

  const login = useCallback(
    (next: Token, persist = true) => {
      saveToken(next, persist);
      setToken(next);
      router.push(homeRouteForRole(next.role));
    },
    [router],
  );

  const logout = useCallback(() => {
    clearToken();
    setToken(null);
    router.push("/login");
  }, [router]);

  const value = useMemo(() => ({ token, ready, login, logout }), [token, ready, login, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
