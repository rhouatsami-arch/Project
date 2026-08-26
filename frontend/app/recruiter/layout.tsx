"use client";

import { CalendarClock, LayoutDashboard, Plus, Users } from "lucide-react";
import { AppHeader, WorkspaceTab } from "@/components/ui";
import { RequireAuth } from "@/components/require-auth";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { api, auth } from "@/lib/api";
import { useAuth } from "@/providers/auth-provider";
import type { Recruiter } from "@/types/recruitment";

export default function RecruiterLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { token } = useAuth();
  const [profile, setProfile] = useState<Recruiter | null>(null);

  useEffect(() => {
    if (!token) return;
    api<Recruiter>("/recruiters/me", auth(token.access_token))
      .then(setProfile)
      .catch(() => setProfile(null));
  }, [token]);

  return (
    <RequireAuth role="recruiter">
      <div className="workspace-shell">
        <AppHeader
          label="Recruiter workspace"
          title={profile?.company_name || "Hiring desk"}
          subtitle="Dashboard, pipeline IA, offres et planification des entretiens."
        />
        <div className="workspace-tabs">
          <WorkspaceTab
            href="/recruiter/dashboard"
            active={pathname === "/recruiter/dashboard"}
          >
            <LayoutDashboard size={18} /> Dashboard
          </WorkspaceTab>
          <WorkspaceTab
            href="/recruiter/pipeline"
            active={pathname === "/recruiter/pipeline"}
          >
            <Users size={18} /> Pipeline
          </WorkspaceTab>
          <WorkspaceTab href="/recruiter/jobs" active={pathname === "/recruiter/jobs"}>
            <Plus size={18} /> Create job
          </WorkspaceTab>
          <WorkspaceTab
            href="/recruiter/meetings"
            active={pathname === "/recruiter/meetings"}
          >
            <CalendarClock size={18} /> Planification
          </WorkspaceTab>
        </div>
        {children}
      </div>
    </RequireAuth>
  );
}
