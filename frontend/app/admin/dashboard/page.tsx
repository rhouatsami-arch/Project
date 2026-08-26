"use client";

import { useCallback, useEffect, useState } from "react";
import { SectionHeading } from "@/components/ui";
import { api, auth, messageFromError } from "@/lib/api";
import { RequireAuth } from "@/components/require-auth";
import { useAuth } from "@/providers/auth-provider";
import { useNotice } from "@/providers/notice-provider";
import type { AdminDashboard } from "@/types/recruitment";

export default function AdminDashboardPage() {
  const { token } = useAuth();
  const { showNotice } = useNotice();
  const [dashboard, setDashboard] = useState<AdminDashboard | null>(null);

  const load = useCallback(async () => {
    if (!token) return;
    setDashboard(await api<AdminDashboard>("/admin/dashboard", auth(token.access_token)));
  }, [token]);

  useEffect(() => {
    load().catch((error) => showNotice(messageFromError(error)));
  }, [load, showNotice]);

  return (
    <RequireAuth role="admin">
      <section className="student-dashboard">
        <SectionHeading
          title="Tableau de bord administrateur"
          text="Supervision des utilisateurs, données, performances et journaux d'audit."
        />
        <div className="dashboard-summary">
          <div className="dashboard-stat"><strong>{dashboard?.total_students ?? 0}</strong><p>Étudiants</p></div>
          <div className="dashboard-stat"><strong>{dashboard?.total_candidates ?? 0}</strong><p>Candidats</p></div>
          <div className="dashboard-stat"><strong>{dashboard?.total_recruiters ?? 0}</strong><p>Recruteurs</p></div>
          <div className="dashboard-stat"><strong>{dashboard?.total_jobs ?? 0}</strong><p>Offres</p></div>
          <div className="dashboard-stat"><strong>{dashboard?.total_applications ?? 0}</strong><p>Candidatures</p></div>
          <div className="dashboard-stat"><strong>{dashboard?.total_meetings ?? 0}</strong><p>Entretiens</p></div>
        </div>
        <div className="job-stack">
          <SectionHeading title="Journaux d'audit récents" text="Traçabilité des actions sur la plateforme." />
          {(dashboard?.recent_audit_logs.length ?? 0) === 0 ? (
            <p>Aucun journal pour le moment.</p>
          ) : (
            dashboard!.recent_audit_logs.map((log) => (
              <article className="job-card" key={log.id}>
                <p className="eyebrow">{log.actor_role} · {log.actor_email}</p>
                <h3>{log.action_label || log.action}</h3>
                <p>{log.details || log.resource || "—"}</p>
                <span>{log.created_at.split("T")[0]}</span>
              </article>
            ))
          )}
        </div>
      </section>
    </RequireAuth>
  );
}
