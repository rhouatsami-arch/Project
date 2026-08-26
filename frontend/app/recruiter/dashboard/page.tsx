"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  BriefcaseBusiness,
  CalendarClock,
  Mail,
  Sparkles,
  Users,
} from "lucide-react";
import { SectionHeading } from "@/components/ui";
import { api, auth, formatDate, messageFromError } from "@/lib/api";
import { useAuth } from "@/providers/auth-provider";
import { useNotice } from "@/providers/notice-provider";
import type { RecruiterDashboard } from "@/types/recruitment";

type NotificationItem = {
  id: number;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
};

export default function RecruiterDashboardPage() {
  const { token } = useAuth();
  const { showNotice } = useNotice();
  const [dashboard, setDashboard] = useState<RecruiterDashboard | null>(null);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);

  const load = useCallback(async () => {
    if (!token) return;
    const headers = auth(token.access_token);
    const [nextDashboard, nextNotifications] = await Promise.all([
      api<RecruiterDashboard>("/recruiters/me/dashboard", headers),
      api<NotificationItem[]>("/llm/recruiters/me/notifications", headers),
    ]);
    setDashboard(nextDashboard);
    setNotifications(nextNotifications);
  }, [token]);

  useEffect(() => {
    load().catch((error) => showNotice(messageFromError(error)));
  }, [load, showNotice]);

  return (
    <section className="student-dashboard">
      <SectionHeading
        title="Tableau de bord recruteur"
        text="Pilotage des offres, candidatures, entretiens et notifications en un coup d'oeil."
      />

      <div className="dashboard-summary">
        <div className="dashboard-stat">
          <strong>{dashboard?.open_jobs ?? 0}</strong>
          <p>Offres ouvertes</p>
        </div>
        <div className="dashboard-stat">
          <strong>{dashboard?.total_applications ?? 0}</strong>
          <p>Candidatures</p>
        </div>
        <div className="dashboard-stat">
          <strong>{dashboard?.shortlisted_count ?? 0}</strong>
          <p>Shortlist</p>
        </div>
        <div className="dashboard-stat">
          <strong>{dashboard?.interview_count ?? 0}</strong>
          <p>Entretiens</p>
        </div>
        <div className="dashboard-stat">
          <strong>{dashboard?.upcoming_meetings ?? 0}</strong>
          <p>Réunions à venir</p>
        </div>
        <div className="dashboard-stat">
          <strong>{dashboard?.average_match_score ?? 0}%</strong>
          <p>Score moyen</p>
        </div>
      </div>

      <div className="home-actions" style={{ marginBottom: "1rem" }}>
        <Link className="primary-button" href="/recruiter/pipeline">
          <Users size={17} /> Ouvrir le pipeline
        </Link>
        <Link className="secondary-button" href="/recruiter/jobs">
          <BriefcaseBusiness size={17} /> Créer une offre
        </Link>
        <Link className="secondary-button" href="/recruiter/meetings">
          <CalendarClock size={17} /> Planifier un entretien
        </Link>
      </div>

      <div className="dashboard-panels">
        <div className="job-stack">
          <SectionHeading
            title="Funnel de recrutement"
            text="Répartition des candidatures par statut."
          />
          <article className="job-card">
            <p>Applied · {dashboard?.applied_count ?? 0}</p>
            <p>Shortlisted · {dashboard?.shortlisted_count ?? 0}</p>
            <p>Interview · {dashboard?.interview_count ?? 0}</p>
            <p>Hired · {dashboard?.hired_count ?? 0}</p>
            <p>Rejected · {dashboard?.rejected_count ?? 0}</p>
            <p>Offres fermées · {dashboard?.closed_jobs ?? 0}</p>
          </article>

          <SectionHeading title="Notifications" text="Alertes liées aux entretiens et au pipeline." />
          {notifications.length === 0 ? (
            <p>Aucune notification pour le moment.</p>
          ) : (
            notifications.slice(0, 5).map((item) => (
              <article className="job-card" key={item.id}>
                <p className="eyebrow">{item.type}</p>
                <h3>{item.title}</h3>
                <p>{item.message}</p>
              </article>
            ))
          )}
        </div>

        <div className="candidate-board">
          <SectionHeading
            title="Candidatures récentes"
            text="Derniers profils entrés dans votre pipeline."
          />
          <div className="candidate-grid">
            {(dashboard?.recent_applications.length ?? 0) === 0 ? (
              <p>Aucune candidature récente.</p>
            ) : (
              dashboard!.recent_applications.map((application) => (
                <article className="candidate-card" key={application.application_id}>
                  <div className="candidate-head">
                    <div>
                      <h3>{application.candidate_name}</h3>
                      <p>{application.job_title}</p>
                    </div>
                    <span className="score">{application.match_score}%</span>
                  </div>
                  <p className="status-line">{application.status}</p>
                  <p>{application.candidate_email}</p>
                  <p>{formatDate(application.created_at)}</p>
                </article>
              ))
            )}
          </div>

          <SectionHeading
            title="Prochains entretiens"
            text="Réunions proposées ou acceptées à venir."
          />
          <div className="candidate-grid">
            {(dashboard?.upcoming_meeting_list.length ?? 0) === 0 ? (
              <p>Aucun entretien planifié.</p>
            ) : (
              dashboard!.upcoming_meeting_list.map((meeting) => (
                <article className="candidate-card" key={meeting.meeting_id}>
                  <div className="candidate-head">
                    <div>
                      <h3>{meeting.candidate_name}</h3>
                      <p>Offre #{meeting.job_id}</p>
                    </div>
                    <Mail size={20} />
                  </div>
                  <p className="status-line">{meeting.status}</p>
                  <p>{formatDate(meeting.scheduled_at)}</p>
                  <p>{meeting.location || "Lieu à confirmer"}</p>
                </article>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="home-cta" style={{ marginTop: "1.25rem" }}>
        <div>
          <p className="eyebrow">Action rapide</p>
          <h2>Utilisez le matching IA pour prioriser les meilleurs profils.</h2>
        </div>
        <Link className="primary-button" href="/recruiter/pipeline">
          <Sparkles size={17} /> Classer les candidats
        </Link>
      </div>
    </section>
  );
}
