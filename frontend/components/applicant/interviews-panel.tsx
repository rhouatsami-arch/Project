"use client";

import { useCallback, useEffect, useState } from "react";
import { CalendarClock, CheckCircle2, Link2, Video, XCircle } from "lucide-react";
import { SectionHeading } from "@/components/ui";
import { api, auth, formatDate, messageFromError } from "@/lib/api";
import type { ApplicantApiBase } from "@/lib/applicant";
import { useAuth } from "@/providers/auth-provider";
import { useNotice } from "@/providers/notice-provider";
import type { CandidateAvailability, Meeting } from "@/types/recruitment";

const STATUS_LABELS: Record<string, string> = {
  proposed: "Proposée",
  accepted: "Acceptée",
  refused: "Refusée",
  completed: "Terminée",
  cancelled: "Annulée",
};

function toLocalInputValue(date: Date) {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function InterviewsPanel({
  apiBase,
  meetingsPath,
  availabilityListPath,
  availabilityCreatePath,
  confirmPath,
  refusePath,
}: {
  apiBase: ApplicantApiBase;
  meetingsPath: string;
  availabilityListPath: string;
  availabilityCreatePath: string;
  confirmPath: (id: number) => string;
  refusePath: (id: number) => string;
}) {
  const { token } = useAuth();
  const { showNotice } = useNotice();
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [windows, setWindows] = useState<CandidateAvailability[]>([]);
  const [startsAt, setStartsAt] = useState(() => toLocalInputValue(new Date(Date.now() + 24 * 3600_000)));
  const [endsAt, setEndsAt] = useState(() => toLocalInputValue(new Date(Date.now() + 28 * 3600_000)));

  const load = useCallback(async () => {
    if (!token) return;
    const headers = auth(token.access_token);
    const [nextMeetings, nextWindows] = await Promise.all([
      api<Meeting[]>(meetingsPath, headers),
      api<CandidateAvailability[]>(availabilityListPath, headers),
    ]);
    setMeetings(nextMeetings);
    setWindows(nextWindows);
  }, [availabilityListPath, meetingsPath, token]);

  useEffect(() => {
    load().catch((error) => showNotice(messageFromError(error)));
  }, [load, showNotice]);

  async function addWindow() {
    if (!token) return;
    try {
      await api(availabilityCreatePath, {
        ...auth(token.access_token),
        method: "POST",
        body: JSON.stringify({
          starts_at: new Date(startsAt).toISOString(),
          ends_at: new Date(endsAt).toISOString(),
        }),
      });
      await load();
      showNotice("Disponibilité enregistrée.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function removeWindow(id: number) {
    if (!token) return;
    const path =
      apiBase === "/candidates"
        ? `/meetings/availability/${id}`
        : `/meetings/students/availability/${id}`;
    try {
      await api(path, { ...auth(token.access_token), method: "DELETE" });
      await load();
      showNotice("Disponibilité supprimée.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function confirm(id: number) {
    if (!token) return;
    try {
      await api(confirmPath(id), { ...auth(token.access_token), method: "POST" });
      await load();
      showNotice("Entretien accepté.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function refuse(id: number) {
    if (!token) return;
    try {
      await api(refusePath(id), { ...auth(token.access_token), method: "POST" });
      await load();
      showNotice("Entretien refusé.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  return (
    <section className="recruiter-pipeline scheduling-desk">
      <div className="candidate-board" style={{ width: "100%" }}>
        <SectionHeading
          title="Mes entretiens"
          text="Indiquez vos disponibilités, puis acceptez ou refusez les créneaux proposés."
        />

        <article className="candidate-card scheduling-panel">
          <div className="candidate-head">
            <div>
              <h3>Mes disponibilités</h3>
              <p>Le recruteur s’appuie sur ces plages pour la proposition automatique.</p>
            </div>
            <CalendarClock size={22} />
          </div>
          <label>
            Début
            <input type="datetime-local" value={startsAt} onChange={(e) => setStartsAt(e.target.value)} />
          </label>
          <label>
            Fin
            <input type="datetime-local" value={endsAt} onChange={(e) => setEndsAt(e.target.value)} />
          </label>
          <button className="primary-button" type="button" onClick={addWindow}>
            Ajouter une disponibilité
          </button>
          <div className="candidate-grid" style={{ marginTop: "1rem" }}>
            {windows.length === 0 ? (
              <p>Aucune disponibilité renseignée.</p>
            ) : (
              windows.map((window) => (
                <div className="status-line" key={window.id} style={{ display: "flex", justifyContent: "space-between", gap: "0.75rem" }}>
                  <span>
                    {formatDate(window.starts_at)} → {formatDate(window.ends_at)}
                  </span>
                  <button className="secondary-button" type="button" onClick={() => removeWindow(window.id)}>
                    Supprimer
                  </button>
                </div>
              ))
            )}
          </div>
        </article>

        <SectionHeading title="Propositions et historique" text="Statuts : proposée, acceptée, refusée, terminée, annulée." />
        <div className="candidate-grid">
          {meetings.length === 0 ? (
            <p>Aucun entretien pour le moment.</p>
          ) : (
            meetings.map((meeting) => (
              <article className="candidate-card" key={meeting.id}>
                <div className="candidate-head">
                  <div>
                    <h3>Entretien #{meeting.id}</h3>
                    <p>
                      Offre {meeting.job_id} · {formatDate(meeting.scheduled_at)}
                    </p>
                  </div>
                  <span className="score">{STATUS_LABELS[meeting.status] || meeting.status}</span>
                </div>
                <p>{meeting.location || "Lieu à confirmer"}</p>
                <p>{meeting.notes || "—"}</p>
                {(meeting.google_meet_link || meeting.google_event_link) && (
                  <div className="card-actions" style={{ marginTop: "0.5rem" }}>
                    {meeting.google_meet_link && (
                      <a className="secondary-button" href={meeting.google_meet_link} target="_blank" rel="noreferrer">
                        <Video size={17} /> Google Meet
                      </a>
                    )}
                    {meeting.google_event_link && (
                      <a className="secondary-button" href={meeting.google_event_link} target="_blank" rel="noreferrer">
                        <Link2 size={17} /> Événement Calendar
                      </a>
                    )}
                  </div>
                )}
                {meeting.status === "proposed" && (
                  <div className="card-actions">
                    <button className="primary-button" type="button" onClick={() => confirm(meeting.id)}>
                      <CheckCircle2 size={17} /> Accepter
                    </button>
                    <button className="secondary-button" type="button" onClick={() => refuse(meeting.id)}>
                      <XCircle size={17} /> Refuser
                    </button>
                  </div>
                )}
              </article>
            ))
          )}
        </div>
      </div>
    </section>
  );
}
