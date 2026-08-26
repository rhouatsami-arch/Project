"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  CalendarClock,
  CheckCircle2,
  ClipboardList,
  Mail,
  Search,
  Sparkles,
  XCircle,
} from "lucide-react";
import { LlmExplanationPanel } from "@/components/llm-explanation-panel";
import { MatchScoreBreakdown } from "@/components/match-score-breakdown";
import { ProfileLine, SectionHeading } from "@/components/ui";
import { api, auth, candidateName, chips, messageFromError } from "@/lib/api";
import { useAuth } from "@/providers/auth-provider";
import { useNotice } from "@/providers/notice-provider";
import type { Job, LlmExplanation, MatchingPipelineInfo, PipelineCandidate } from "@/types/recruitment";

const STATUS_OPTIONS = [
  { value: "", label: "Tous les statuts" },
  { value: "applied", label: "Applied" },
  { value: "shortlisted", label: "Shortlisted" },
  { value: "interview_invited", label: "Interview" },
  { value: "hired", label: "Hired" },
  { value: "rejected", label: "Rejected" },
];

export default function RecruiterPipelinePage() {
  const { token } = useAuth();
  const { showNotice } = useNotice();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [candidates, setCandidates] = useState<PipelineCandidate[]>([]);
  const [llmInsights, setLlmInsights] = useState<Record<number, LlmExplanation>>({});
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [minScore, setMinScore] = useState(0);
  const [pipelineInfo, setPipelineInfo] = useState<MatchingPipelineInfo | null>(null);

  const loadCandidates = useCallback(
    async (jobId: number) => {
      if (!token) return;
      const params = new URLSearchParams();
      if (minScore > 0) params.set("min_score", String(minScore));
      if (statusFilter) params.set("status_filter", statusFilter);
      const query = params.toString();
      setCandidates(
        await api<PipelineCandidate[]>(
          `/recruiters/jobs/${jobId}/candidates${query ? `?${query}` : ""}`,
          auth(token.access_token),
        ),
      );
    },
    [minScore, statusFilter, token],
  );

  const refresh = useCallback(async () => {
    if (!token) return;
    const headers = auth(token.access_token);
    const [myJobs, pipeline] = await Promise.all([
      api<Job[]>("/jobs/recruiter/me", headers),
      api<MatchingPipelineInfo>("/matching/pipeline", headers),
    ]);
    setJobs(myJobs);
    setPipelineInfo(pipeline);
    setSelectedJobId((current) => {
      if (current && myJobs.some((job) => job.id === current)) return current;
      return myJobs[0]?.id ?? null;
    });
  }, [token]);

  useEffect(() => {
    refresh().catch((error) => showNotice(messageFromError(error)));
  }, [refresh, showNotice]);

  useEffect(() => {
    if (!selectedJobId) return;
    loadCandidates(selectedJobId).catch((error) => showNotice(messageFromError(error)));
  }, [loadCandidates, selectedJobId, showNotice]);

  const filteredCandidates = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) return candidates;
    return candidates.filter((candidate) => {
      const haystack = [
        candidate.first_name,
        candidate.last_name,
        candidate.email,
        candidate.university || "",
        candidate.technical_skills || "",
        candidate.skills || "",
      ]
        .join(" ")
        .toLowerCase();
      return haystack.includes(query);
    });
  }, [candidates, searchQuery]);

  async function shortlist(applicationId: number) {
    if (!token) return;
    try {
      await api(`/recruiters/applications/${applicationId}/shortlist`, {
        ...auth(token.access_token),
        method: "POST",
      });
      if (selectedJobId) await loadCandidates(selectedJobId);
      showNotice("Candidat shortlisté.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function reject(applicationId: number) {
    if (!token) return;
    try {
      await api(`/recruiters/applications/${applicationId}/reject`, {
        ...auth(token.access_token),
        method: "POST",
      });
      if (selectedJobId) await loadCandidates(selectedJobId);
      showNotice("Candidature refusée.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function hire(applicationId: number) {
    if (!token) return;
    try {
      await api(`/recruiters/applications/${applicationId}/hire`, {
        ...auth(token.access_token),
        method: "POST",
      });
      if (selectedJobId) await loadCandidates(selectedJobId);
      showNotice("Candidat marqué comme embauché.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function loadLlmExplain(applicationId: number) {
    if (!token || llmInsights[applicationId]) return;
    try {
      const insight = await api<LlmExplanation>(
        `/llm/recruiters/applications/${applicationId}/explain`,
        auth(token.access_token),
      );
      setLlmInsights((current) => ({ ...current, [applicationId]: insight }));
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function invite(applicationId: number) {
    if (!token) return;
    try {
      await api("/meetings/propose-best", {
        ...auth(token.access_token),
        method: "POST",
        body: JSON.stringify({
          application_id: applicationId,
          location: "Visio / à confirmer",
          notes: "Proposition automatique du meilleur créneau commun.",
        }),
      });
      if (selectedJobId) await loadCandidates(selectedJobId);
      showNotice("Meilleur créneau proposé (planification intelligente).");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  return (
    <section className="recruiter-pipeline">
      <aside className="job-stack">
        <SectionHeading title="Open roles" text={`${jobs.length} roles in this workspace`} />
        {jobs.map((job) => (
          <button
            className={`job-row ${selectedJobId === job.id ? "active" : ""}`}
            key={job.id}
            type="button"
            onClick={() => {
              setSelectedJobId(job.id);
              loadCandidates(job.id).catch((error) => showNotice(messageFromError(error)));
            }}
          >
            <strong>{job.title}</strong>
            <span>{job.required_skills || "No skills listed"}</span>
          </button>
        ))}
      </aside>
      <div className="candidate-board">
        <SectionHeading
          title="Pipeline candidats"
          text="Moteur ML/NLP : score de compatibilité, classement IA, shortlist et entretiens."
        />

        {pipelineInfo && (
          <details className="pipeline-ia-panel">
            <summary>
              Pipeline IA · {pipelineInfo.title} v{pipelineInfo.version}
            </summary>
            <p>{pipelineInfo.description}</p>
            <p className="pipeline-formula">{pipelineInfo.formula}</p>
            <ol>
              {pipelineInfo.stages.map((stage) => (
                <li key={stage.name}>
                  <strong>{stage.name}</strong> — {stage.description}
                  <span> ({stage.technique})</span>
                </li>
              ))}
            </ol>
            <div className="chips">
              {pipelineInfo.algorithms.map((algo) => (
                <span key={algo}>{algo}</span>
              ))}
            </div>
          </details>
        )}

        <div className="jobs-toolbar">
          <label className="field" style={{ flex: 1 }}>
            <span>Recherche</span>
            <div style={{ position: "relative" }}>
              <Search
                size={16}
                style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)" }}
              />
              <input
                style={{ paddingLeft: 36 }}
                placeholder="Nom, email, compétences..."
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
              />
            </div>
          </label>
          <label className="field">
            <span>Statut</span>
            <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              {STATUS_OPTIONS.map((option) => (
                <option key={option.value || "all"} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Score min.</span>
            <select
              value={minScore}
              onChange={(event) => setMinScore(Number(event.target.value))}
            >
              <option value={0}>0%</option>
              <option value={40}>40%</option>
              <option value={60}>60%</option>
              <option value={75}>75%</option>
            </select>
          </label>
        </div>

        <div className="candidate-grid">
          {filteredCandidates.length === 0 ? (
            <p>Aucun candidat pour ces filtres.</p>
          ) : (
            filteredCandidates.map((candidate) => (
              <article className="candidate-card" key={candidate.application_id}>
                <div className="candidate-head">
                  <div>
                    <p className="eyebrow">
                      {candidate.rank ? `#${candidate.rank}` : "IA"} ·{" "}
                      {candidate.rank_label || "Score de compatibilité"}
                    </p>
                    <h3>{candidateName(candidate)}</h3>
                    <p>{candidate.email}</p>
                  </div>
                  <span className="score">{candidate.match_score}%</span>
                </div>
                <div className="chips">
                  {chips(candidate.technical_skills || candidate.skills).map((chip) => (
                    <span key={chip}>{chip}</span>
                  ))}
                </div>
                <ProfileLine icon={<Sparkles size={16} />} label="Soft" value={candidate.soft_skills} />
                <ProfileLine icon={<ClipboardList size={16} />} label="Projects" value={candidate.projects} />
                <ProfileLine
                  icon={<CalendarClock size={16} />}
                  label="Experience"
                  value={candidate.experiences}
                />
                {candidate.breakdown && (
                  <details>
                    <summary>Score ML/NLP détaillé</summary>
                    <MatchScoreBreakdown
                      breakdown={candidate.breakdown}
                      explanation={candidate.explanation}
                    />
                  </details>
                )}
                <p className="status-line">{candidate.application_status}</p>
                <button
                  className="secondary-button"
                  type="button"
                  onClick={() => loadLlmExplain(candidate.application_id)}
                >
                  <Sparkles size={17} /> Explication IA
                </button>
                {llmInsights[candidate.application_id] && (
                  <LlmExplanationPanel insight={llmInsights[candidate.application_id]} />
                )}
                <div className="card-actions">
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => shortlist(candidate.application_id)}
                  >
                    <CalendarClock size={17} /> Shortlist
                  </button>
                  <button
                    className="primary-button"
                    type="button"
                    onClick={() => invite(candidate.application_id)}
                  >
                    <Mail size={17} /> Proposer créneau
                  </button>
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => hire(candidate.application_id)}
                  >
                    <CheckCircle2 size={17} /> Embaucher
                  </button>
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => reject(candidate.application_id)}
                  >
                    <XCircle size={17} /> Refuser
                  </button>
                </div>
              </article>
            ))
          )}
        </div>
      </div>
    </section>
  );
}
