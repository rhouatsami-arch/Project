"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Filter, Send, Sparkles, Star } from "lucide-react";
import { LlmExplanationPanel } from "@/components/llm-explanation-panel";
import { MatchScoreBreakdown } from "@/components/match-score-breakdown";
import { api, auth, chips, messageFromError, stripEmpty } from "@/lib/api";
import type { ApplicantApiBase } from "@/lib/applicant";
import { matchingApiBase } from "@/lib/applicant";
import { useAuth } from "@/providers/auth-provider";
import { useNotice } from "@/providers/notice-provider";
import type { Application, Job, JobRecommendation, LlmExplanation, SavedJob, StudentDashboard } from "@/types/recruitment";

export function ApplicantJobsPanel({ apiBase }: { apiBase: ApplicantApiBase }) {
  const { token } = useAuth();
  const { showNotice } = useNotice();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [recommendations, setRecommendations] = useState<JobRecommendation[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [savedJobs, setSavedJobs] = useState<SavedJob[]>([]);
  const [filters, setFilters] = useState({ search: "", location: "", skill: "" });
  const [llmInsights, setLlmInsights] = useState<Record<number, LlmExplanation>>({});

  const refresh = useCallback(async () => {
    if (!token) return;
    const query = new URLSearchParams(stripEmpty(filters));
    const [jobList, dashboardData, recommended] = await Promise.all([
      api<Job[]>(`/jobs/?${query}`, auth(token.access_token)),
      api<StudentDashboard>(`${apiBase}/me/dashboard`, auth(token.access_token)),
      api<JobRecommendation[]>(`${matchingApiBase(apiBase)}/me/recommendations?limit=5&min_score=30`, auth(token.access_token)),
    ]);
    setJobs(jobList);
    setApplications(dashboardData.applications);
    setSavedJobs(dashboardData.saved_jobs);
    setRecommendations(recommended);
  }, [apiBase, filters, token]);

  useEffect(() => {
    refresh().catch((error) => showNotice(messageFromError(error)));
  }, [refresh, showNotice]);

  async function apply(jobId: number) {
    if (!token) return;
    try {
      await api(`${apiBase}/jobs/${jobId}/apply`, {
        ...auth(token.access_token),
        method: "POST",
        body: JSON.stringify({ cover_letter: "" }),
      });
      await refresh();
      showNotice("Application sent.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function save(jobId: number) {
    if (!token) return;
    try {
      await api(`${apiBase}/jobs/${jobId}/save`, { ...auth(token.access_token), method: "POST" });
      await refresh();
      showNotice("Job saved.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function loadLlmInsight(jobId: number) {
    if (!token || llmInsights[jobId]) return;
    try {
      const path =
        apiBase === "/candidates"
          ? `/llm/candidates/me/explain-job/${jobId}`
          : `/llm/students/me/explain-job/${jobId}`;
      const insight = await api<LlmExplanation>(path, auth(token.access_token));
      setLlmInsights((current) => ({ ...current, [jobId]: insight }));
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }
  const appliedIds = useMemo(() => new Set(applications.map((application) => application.job_id)), [applications]);
  const savedIds = useMemo(() => new Set(savedJobs.map((saved) => saved.job.id)), [savedJobs]);

  return (
    <section className="jobs-experience">
      {recommendations.length > 0 && (
        <div className="job-stack" style={{ marginBottom: "2rem" }}>
          <div>
            <p className="eyebrow">ML/NLP recommendations</p>
            <h2>Top matches for your profile</h2>
            <p>Ranked by compatibility score: skills, CV semantics, profile alignment and internship fit.</p>
          </div>
          <div className="jobs-grid">
            {recommendations.map((item) => (
              <article className="job-card" key={item.job.id}>
                <p className="eyebrow">
                  <Sparkles size={14} style={{ display: "inline", verticalAlign: "middle" }} /> {item.rank_label}
                </p>
                <h3>{item.job.title}</h3>
                <p>{item.job.description}</p>
                <p style={{ fontSize: "0.9rem", marginTop: "0.5rem" }}>{item.explanation}</p>
                <button
                  className="secondary-button"
                  type="button"
                  style={{ marginTop: "0.5rem" }}
                  onClick={() => loadLlmInsight(item.job.id)}
                >
                  Voir explication LLM complète
                </button>
                {llmInsights[item.job.id] && <LlmExplanationPanel insight={llmInsights[item.job.id]} />}
                <details style={{ marginTop: "0.5rem" }}>
                  <summary>Score ML/NLP (6 critères)</summary>
                  <MatchScoreBreakdown breakdown={item.breakdown} />
                </details>
                <div className="chips">
                  {chips(item.job.required_skills).map((chip) => (
                    <span key={chip}>{chip}</span>
                  ))}
                </div>
                <div className="card-actions">
                  <span className="score">{item.compatibility_score}%</span>
                  <button className="primary-button" type="button" disabled={appliedIds.has(item.job.id)} onClick={() => apply(item.job.id)}>
                    <Send size={17} /> {appliedIds.has(item.job.id) ? "Applied" : "Apply"}
                  </button>
                </div>
              </article>
            ))}
          </div>
        </div>
      )}

      <div className="jobs-toolbar">
        <div>
          <p className="eyebrow">Opportunities</p>
          <h2>Available jobs</h2>
        </div>
        <div className="filter-bar">
          <input placeholder="Search" value={filters.search} onChange={(event) => setFilters({ ...filters, search: event.target.value })} />
          <input placeholder="Location" value={filters.location} onChange={(event) => setFilters({ ...filters, location: event.target.value })} />
          <input placeholder="Skill" value={filters.skill} onChange={(event) => setFilters({ ...filters, skill: event.target.value })} />
          <button className="icon-button" type="button" onClick={() => refresh().catch((error) => showNotice(messageFromError(error)))}>
            <Filter size={18} />
          </button>
        </div>
      </div>
      <div className="jobs-grid">
        {jobs.map((job) => (
          <article className="job-card" key={job.id}>
            <p className="eyebrow">
              {job.location || "Remote"} · {job.employment_type || "full time"}
            </p>
            <h3>{job.title}</h3>
            <p>{job.description}</p>
            <div className="chips">
              {chips(job.required_skills).map((chip) => (
                <span key={chip}>{chip}</span>
              ))}
            </div>
            <div className="card-actions">
              <button className="secondary-button" type="button" disabled={savedIds.has(job.id)} onClick={() => save(job.id)}>
                <Star size={17} /> {savedIds.has(job.id) ? "Saved" : "Save"}
              </button>
              <button className="primary-button" type="button" disabled={appliedIds.has(job.id)} onClick={() => apply(job.id)}>
                <Send size={17} /> {appliedIds.has(job.id) ? "Applied" : "Apply"}
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
