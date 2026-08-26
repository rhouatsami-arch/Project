"use client";

import { LayoutDashboard, ScrollText, Users } from "lucide-react";
import { AppHeader, WorkspaceTab } from "@/components/ui";
import { RequireAuth } from "@/components/require-auth";
import { usePathname } from "next/navigation";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <RequireAuth role="admin">
      <div className="workspace-shell">
        <AppHeader
          label="Administration"
          title="MatiousHire Control"
          subtitle="Gestion des utilisateurs, supervision des données, performances et journaux d'audit."
        />
        <div className="workspace-tabs">
          <WorkspaceTab href="/admin/dashboard" active={pathname === "/admin/dashboard"}>
            <LayoutDashboard size={18} /> Dashboard
          </WorkspaceTab>
          <WorkspaceTab href="/admin/users" active={pathname === "/admin/users"}>
            <Users size={18} /> Users
          </WorkspaceTab>
          <WorkspaceTab href="/admin/audit-logs" active={pathname === "/admin/audit-logs"}>
            <ScrollText size={18} /> Audit logs
          </WorkspaceTab>
        </div>
        {children}
      </div>
    </RequireAuth>
  );
}
