"use client";

import { Suspense, useCallback, useEffect, useMemo, useState } from "react";
import { CalendarClock, CheckCircle2, Clock3, Link2, Video, XCircle } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { SectionHeading } from "@/components/ui";
import { api, auth, formatDate, messageFromError } from "@/lib/api";
import { useAuth } from "@/providers/auth-provider";
import { useNotice } from "@/providers/notice-provider";
import type { GoogleCalendarStatus, InterviewSlot, Meeting } from "@/types/recruitment";

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

function RecruiterMeetingsPageContent() {
  const { token } = useAuth();
  const { showNotice } = useNotice();
  const searchParams = useSearchParams();
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [slots, setSlots] = useState<InterviewSlot[]>([]);
  const [calendarStatus, setCalendarStatus] = useState<GoogleCalendarStatus | null>(null);
  const [startsAt, setStartsAt] = useState(() => toLocalInputValue(new Date(Date.now() + 24 * 3600_000)));
  const [endsAt, setEndsAt] = useState(() => toLocalInputValue(new Date(Date.now() + 25 * 3600_000)));
  const [proposeAppId, setProposeAppId] = useState("");
  const [rescheduleId, setRescheduleId] = useState<number | null>(null);
  const [rescheduleAt, setRescheduleAt] = useState("");

  const load = useCallback(async () => {
    if (!token) return;
    const headers = auth(token.access_token);
    const [nextMeetings, nextSlots, nextCalendar] = await Promise.all([
      api<Meeting[]>("/meetings/recruiter/me", headers),
      api<InterviewSlot[]>("/meetings/slots/me", headers),
      api<GoogleCalendarStatus>("/meetings/google/status", headers).catch(() => null),
    ]);
    setMeetings(nextMeetings);
    setSlots(nextSlots);
    setCalendarStatus(nextCalendar);
  }, [token]);

  useEffect(() => {
    load().catch((error) => showNotice(messageFromError(error)));
  }, [load, showNotice]);

  useEffect(() => {
    const result = searchParams.get("google_calendar");
    if (result === "connected") {
      showNotice("Google Calendar connecté. Les entretiens acceptés seront synchronisés.");
    } else if (result === "error") {
      showNotice("Connexion Google Calendar annulée ou échouée.");
    }
  }, [searchParams, showNotice]);

  const history = useMemo(
    () => meetings.filter((m) => ["completed", "cancelled", "refused"].includes(m.status)),
    [meetings],
  );
  const active = useMemo(
    () => meetings.filter((m) => ["proposed", "accepted"].includes(m.status)),
    [meetings],
  );

  async function createSlot() {
    if (!token) return;
    try {
      await api("/meetings/slots", {
        ...auth(token.access_token),
        method: "POST",
        body: JSON.stringify({
          starts_at: new Date(startsAt).toISOString(),
          ends_at: new Date(endsAt).toISOString(),
        }),
      });
      await load();
      showNotice("Créneau recruteur ajouté.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function removeSlot(slotId: number) {
    if (!token) return;
    try {
      await api(`/meetings/slots/${slotId}`, {
        ...auth(token.access_token),
        method: "DELETE",
      });
      await load();
      showNotice("Créneau supprimé.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function proposeBest() {
    if (!token || !proposeAppId) return;
    try {
      await api("/meetings/propose-best", {
        ...auth(token.access_token),
        method: "POST",
        body: JSON.stringify({
          application_id: Number(proposeAppId),
          location: "Visio / à confirmer",
          notes: "Proposition automatique du meilleur créneau commun.",
        }),
      });
      await load();
      showNotice("Meilleur créneau proposé au candidat.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function cancelMeeting(id: number) {
    if (!token) return;
    try {
      await api(`/meetings/${id}/cancel`, { ...auth(token.access_token), method: "POST" });
      await load();
      showNotice("Entretien annulé.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function completeMeeting(id: number) {
    if (!token) return;
    try {
      await api(`/meetings/${id}/complete`, { ...auth(token.access_token), method: "POST" });
      await load();
      showNotice("Entretien marqué terminé.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function rescheduleMeeting(id: number) {
    if (!token || !rescheduleAt) return;
    try {
      await api(`/meetings/${id}/reschedule`, {
        ...auth(token.access_token),
        method: "POST",
        body: JSON.stringify({ scheduled_at: new Date(rescheduleAt).toISOString() }),
      });
      setRescheduleId(null);
      setRescheduleAt("");
      await load();
      showNotice("Entretien reprogrammé (statut : proposée).");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function connectGoogleCalendar() {
    if (!token) return;
    try {
      const { authorization_url } = await api<{ authorization_url: string }>(
        "/meetings/google/authorize",
        auth(token.access_token),
      );
      window.location.href = authorization_url;
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function disconnectGoogleCalendar() {
    if (!token) return;
    try {
      await api("/meetings/google/disconnect", {
        ...auth(token.access_token),
        method: "DELETE",
      });
      await load();
      showNotice("Google Calendar déconnecté.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  return (
    <section className="recruiter-pipeline scheduling-desk">
      <div className="candidate-board" style={{ width: "100%" }}>
        <SectionHeading
          title="Planification intelligente des entretiens"
          text="Simplifiez l'organisation : créneaux recruteur, disponibilités candidat, meilleure proposition, confirmation et synchronisation Google Calendar."
        />

        <article className="candidate-card scheduling-panel" style={{ marginBottom: "1rem" }}>
          <div className="candidate-head">
            <div>
              <h3>Google Calendar</h3>
              <p>
                {calendarStatus?.connected
                  ? `Connecté${calendarStatus.google_email ? ` (${calendarStatus.google_email})` : ""}.`
                  : calendarStatus?.configured
                    ? "Connectez votre agenda pour créer automatiquement les événements (avec lien Google Meet) quand un candidat accepte."
                    : "Non configuré côté serveur (GOOGLE_CALENDAR_* ou GOOGLE_CLIENT_* dans .env)."}
              </p>
            </div>
            <CalendarClock size={22} />
          </div>
          {calendarStatus?.configured && (
            <div className="card-actions">
              {calendarStatus.connected ? (
                <button className="secondary-button" type="button" onClick={disconnectGoogleCalendar}>
                  Déconnecter Google Calendar
                </button>
              ) : (
                <button className="primary-button" type="button" onClick={connectGoogleCalendar}>
                  Connecter Google Calendar
                </button>
              )}
            </div>
          )}
        </article>

        <div className="scheduling-grid">
          <article className="candidate-card scheduling-panel">
            <div className="candidate-head">
              <div>
                <h3>Créneaux disponibles</h3>
                <p>Ajoutez vos plages libres pour les entretiens.</p>
              </div>
              <Clock3 size={22} />
            </div>
            <label>
              Début
              <input type="datetime-local" value={startsAt} onChange={(e) => setStartsAt(e.target.value)} />
            </label>
            <label>
              Fin
              <input type="datetime-local" value={endsAt} onChange={(e) => setEndsAt(e.target.value)} />
            </label>
            <button className="primary-button" type="button" onClick={createSlot}>
              Ajouter un créneau
            </button>
            <div className="candidate-grid" style={{ marginTop: "1rem" }}>
              {slots.length === 0 ? (
                <p>Aucun créneau. Créez vos disponibilités pour activer la proposition automatique.</p>
              ) : (
                slots.map((slot) => (
                  <div className="status-line" key={slot.id} style={{ display: "flex", justifyContent: "space-between", gap: "0.75rem" }}>
                    <span>
                      {formatDate(slot.starts_at)} → {formatDate(slot.ends_at)}
                      {slot.is_booked ? " · réservé" : " · libre"}
                    </span>
                    {!slot.is_booked && (
                      <button className="secondary-button" type="button" onClick={() => removeSlot(slot.id)}>
                        Supprimer
                      </button>
                    )}
                  </div>
                ))
              )}
            </div>
          </article>

          <article className="candidate-card scheduling-panel">
            <div className="candidate-head">
              <div>
                <h3>Proposition automatique</h3>
                <p>Calcule le meilleur chevauchement créneau × disponibilité candidat.</p>
              </div>
              <CalendarClock size={22} />
            </div>
            <label>
              ID candidature
              <input
                type="number"
                min={1}
                placeholder="ex. depuis le pipeline"
                value={proposeAppId}
                onChange={(e) => setProposeAppId(e.target.value)}
              />
            </label>
            <button className="primary-button" type="button" onClick={proposeBest} disabled={!proposeAppId}>
              Proposer le meilleur créneau
            </button>
            <p className="status-line" style={{ marginTop: "0.75rem" }}>
              Statuts : proposée, acceptée, refusée, terminée, annulée. À l&apos;acceptation, l&apos;événement est créé dans Google Calendar si connecté.
            </p>
          </article>
        </div>

        <SectionHeading title="Réunions en cours" text="Confirmation, reprogrammation et clôture." />
        <div className="candidate-grid">
          {active.length === 0 ? (
            <p>Aucune réunion active. Proposez un créneau depuis le pipeline ou le formulaire ci-dessus.</p>
          ) : (
            active.map((meeting) => (
              <article className="candidate-card" key={meeting.id}>
                <div className="candidate-head">
                  <div>
                    <h3>Entretien #{meeting.id}</h3>
                    <p>
                      Candidature {meeting.application_id} · Offre {meeting.job_id}
                    </p>
                  </div>
                  <span className="score">{STATUS_LABELS[meeting.status] || meeting.status}</span>
                </div>
                <p className="status-line">{formatDate(meeting.scheduled_at)}</p>
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
                <div className="card-actions">
                  {meeting.status === "accepted" && (
                    <button className="primary-button" type="button" onClick={() => completeMeeting(meeting.id)}>
                      <CheckCircle2 size={17} /> Terminer
                    </button>
                  )}
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => {
                      setRescheduleId(meeting.id);
                      setRescheduleAt(toLocalInputValue(new Date(meeting.scheduled_at)));
                    }}
                  >
                    Reprogrammer
                  </button>
                  <button className="secondary-button" type="button" onClick={() => cancelMeeting(meeting.id)}>
                    <XCircle size={17} /> Annuler
                  </button>
                </div>
                {rescheduleId === meeting.id && (
                  <div style={{ marginTop: "0.75rem", display: "grid", gap: "0.5rem" }}>
                    <input type="datetime-local" value={rescheduleAt} onChange={(e) => setRescheduleAt(e.target.value)} />
                    <button className="primary-button" type="button" onClick={() => rescheduleMeeting(meeting.id)}>
                      Confirmer la reprogrammation
                    </button>
                  </div>
                )}
              </article>
            ))
          )}
        </div>

        <SectionHeading title="Historique des réunions" text="Entretiens terminés, refusés ou annulés." />
        <div className="candidate-grid">
          {history.length === 0 ? (
            <p>Historique vide pour le moment.</p>
          ) : (
            history.map((meeting) => (
              <article className="candidate-card" key={meeting.id}>
                <div className="candidate-head">
                  <div>
                    <h3>Entretien #{meeting.id}</h3>
                    <p>
                      Candidature {meeting.application_id} · {formatDate(meeting.scheduled_at)}
                    </p>
                  </div>
                  <span className="score">{STATUS_LABELS[meeting.status] || meeting.status}</span>
                </div>
              </article>
            ))
          )}
        </div>
      </div>
    </section>
  );
}

export default function RecruiterMeetingsPage() {
  return (
    <Suspense fallback={<section className="recruiter-pipeline scheduling-desk"><div className="candidate-board" style={{ width: "100%" }}><p className="status-line">Chargement de la planification...</p></div></section>}>
      <RecruiterMeetingsPageContent />
    </Suspense>
  );
}
