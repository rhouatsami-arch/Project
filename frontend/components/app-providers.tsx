"use client";

import { AuthProvider } from "@/providers/auth-provider";
import { NoticeProvider } from "@/providers/notice-provider";
import { ThemeProvider } from "@/providers/theme-provider";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <AuthProvider>
        <NoticeProvider>
          <main className="app-shell">{children}</main>
        </NoticeProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
