"use client";

import { BriefcaseBusiness, CalendarClock, LayoutDashboard, UserRound } from "lucide-react";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { AppHeader, WorkspaceTab } from "@/components/ui";
import { RequireAuth } from "@/components/require-auth";
import { api, auth } from "@/lib/api";
import type { ApplicantApiBase } from "@/lib/applicant";
import { useAuth } from "@/providers/auth-provider";
import type { Role } from "@/types/recruitment";
import type { CandidateProfile, Student } from "@/types/recruitment";

type ApplicantLayoutConfig = {
  role: Extract<Role, "student" | "candidate">;
  apiBase: ApplicantApiBase;
  label: string;
  subtitle: string;
  basePath: string;
};

export function ApplicantLayout({
  config,
  children,
}: {
  config: ApplicantLayoutConfig;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { token } = useAuth();
  const [profile, setProfile] = useState<Student | CandidateProfile | null>(null);

  useEffect(() => {
    if (!token) return;
    api<Student | CandidateProfile>(`${config.apiBase}/me`, auth(token.access_token))
      .then(setProfile)
      .catch(() => setProfile(null));
  }, [config.apiBase, token]);

  return (
    <RequireAuth role={config.role}>
      <div className="workspace-shell">
        <AppHeader
          label={config.label}
          title={profile ? `${profile.first_name} ${profile.last_name}` : config.label}
          subtitle={config.subtitle}
        />
        <div className="workspace-tabs">
          <WorkspaceTab href={`${config.basePath}/profile`} active={pathname === `${config.basePath}/profile`}>
            <UserRound size={18} /> Profile
          </WorkspaceTab>
          <WorkspaceTab href={`${config.basePath}/dashboard`} active={pathname === `${config.basePath}/dashboard`}>
            <LayoutDashboard size={18} /> Dashboard
          </WorkspaceTab>
          <WorkspaceTab href={`${config.basePath}/jobs`} active={pathname === `${config.basePath}/jobs`}>
            <BriefcaseBusiness size={18} /> Jobs
          </WorkspaceTab>
          <WorkspaceTab href={`${config.basePath}/interviews`} active={pathname === `${config.basePath}/interviews`}>
            <CalendarClock size={18} /> Entretiens
          </WorkspaceTab>
        </div>
        {children}
      </div>
    </RequireAuth>
  );
}
