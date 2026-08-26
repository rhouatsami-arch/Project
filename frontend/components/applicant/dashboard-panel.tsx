"use client";

import { useCallback, useEffect, useState } from "react";
import { SectionHeading } from "@/components/ui";
import { api, auth, formatDate, messageFromError } from "@/lib/api";
import type { ApplicantApiBase } from "@/lib/applicant";
import { useAuth } from "@/providers/auth-provider";
import { useNotice } from "@/providers/notice-provider";
import type { CandidateDashboard, StudentDashboard } from "@/types/recruitment";

export function ApplicantDashboardPanel({ apiBase }: { apiBase: ApplicantApiBase }) {
  const { token } = useAuth();
  const { showNotice } = useNotice();
  const [dashboard, setDashboard] = useState<StudentDashboard | CandidateDashboard | null>(null);

  const loadDashboard = useCallback(async () => {
    if (!token) return;
    setDashboard(await api<StudentDashboard>(`${apiBase}/me/dashboard`, auth(token.access_token)));
  }, [apiBase, token]);

  useEffect(() => {
    loadDashboard().catch((error) => showNotice(messageFromError(error)));
  }, [loadDashboard, showNotice]);

  return (
    <section className="student-dashboard">
      <div className="dashboard-summary">
        <div className="dashboard-stat">
          <strong>{dashboard?.total_applications ?? 0}</strong>
          <p>Applications submitted</p>
        </div>
        <div className="dashboard-stat">
          <strong>{dashboard?.interview_invites ?? 0}</strong>
          <p>Interview invites</p>
        </div>
        <div className="dashboard-stat">
          <strong>{dashboard?.saved_jobs_count ?? 0}</strong>
          <p>Saved jobs</p>
        </div>
        <div className="dashboard-stat">
          <strong>
            {dashboard?.applications.length
              ? Math.round(dashboard.applications.reduce((sum, item) => sum + item.match_score, 0) / dashboard.applications.length)
              : 0}
            %
          </strong>
          <p>Average match score</p>
        </div>
      </div>

      <div className="dashboard-panels">
        <div className="job-stack">
          <SectionHeading title="Your applications" text="Track every submission and upcoming interview." />
          {(dashboard?.applications.length ?? 0) === 0 ? (
            <p>No applications yet. Apply to a role to get started.</p>
          ) : (
            dashboard!.applications.map((application) => (
              <article className="job-card" key={application.id}>
                <p className="eyebrow">
                  {application.job_location || "Remote"} · {application.job_employment_type || "full time"}
                </p>
                <h3>{application.job_title}</h3>
                <p>Status: {application.status.replaceAll("_", " ")}</p>
                {application.interview_at && <p className="status-line">Interview scheduled {formatDate(application.interview_at)}</p>}
                <div className="card-actions">
                  <span className="score">{application.match_score}%</span>
                  <span>{application.created_at.split("T")[0]}</span>
                </div>
              </article>
            ))
          )}
        </div>

        <aside className="job-stack">
          <SectionHeading title="Saved jobs" text="Keep the roles you want to revisit close at hand." />
          {(dashboard?.saved_jobs.length ?? 0) === 0 ? (
            <p>No saved jobs yet. Use Save on the jobs tab.</p>
          ) : (
            dashboard!.saved_jobs.map((saved) => (
              <button className="job-row" key={saved.id} type="button" disabled>
                <strong>{saved.job.title}</strong>
                <span>{saved.job.location || "Remote"}</span>
              </button>
            ))
          )}
        </aside>
      </div>
    </section>
  );
}
